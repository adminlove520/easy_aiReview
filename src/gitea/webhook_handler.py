import os
import re
import time
from urllib.parse import urljoin
import fnmatch
import requests

from src.utils.log import logger


def filter_changes(changes: list):
    '''
    过滤数据，只保留支持的文件类型以及必要的字段信息
    复用 GitLab 的 filter_changes 逻辑（格式相同）
    '''
    # 从环境变量中获取支持的文件扩展名
    supported_extensions = os.getenv('SUPPORTED_EXTENSIONS', '.java,.py,.php').split(',')

    filter_deleted_files_changes = [change for change in changes if not change.get("deleted_file")]

    # 过滤 `new_path` 以支持的扩展名结尾的元素, 仅保留diff和new_path字段
    filtered_changes = []
    for item in filter_deleted_files_changes:
        new_path = item.get('new_path', '')
        if not new_path:
            continue
        
        # 检查文件扩展名
        if not any(new_path.endswith(ext) for ext in supported_extensions):
            continue
        
        # 优先使用已有的 additions 和 deletions 值（如果存在）
        additions = item.get('additions', 0)
        deletions = item.get('deletions', 0)
        
        # 如果没有提供，尝试从 diff 中计算
        diff_content = item.get('diff', '')
        if additions == 0 and deletions == 0 and diff_content:
            additions = len(re.findall(r'^\+(?!\+\+)', diff_content, re.MULTILINE))
            deletions = len(re.findall(r'^-(?!--)', diff_content, re.MULTILINE))
        
        filtered_changes.append({
            'diff': diff_content,
            'new_path': new_path,
            'additions': additions,
            'deletions': deletions
        })
    
    logger.debug(f"filter_changes: filtered {len(filtered_changes)} files from {len(changes)} changes")
    return filtered_changes


class PushHandler:
    def __init__(self, webhook_data: dict, gitea_token: str, gitea_url: str):
        self.webhook_data = webhook_data
        self.gitea_token = gitea_token
        self.gitea_url = gitea_url
        self.event_type = None
        self.repo_full_name = None
        self.branch_name = None
        self.commit_list = []
        self.parse_event_type()

    def parse_event_type(self):
        # 提取 event_type
        self.event_type = 'push'  # Gitea webhook 的事件类型通过 header 中的 X-Gitea-Event 获取，API 中已处理
        self.parse_push_event()

    def parse_push_event(self):
        # 提取 Push 事件的相关参数
        repository = self.webhook_data.get('repository', {})
        # 优先使用 full_name，如果没有则使用 owner.login + '/' + name
        self.repo_full_name = repository.get('full_name')
        if not self.repo_full_name:
            owner = repository.get('owner', {})
            owner_login = owner.get('login', '')
            repo_name = repository.get('name', '')
            if owner_login and repo_name:
                self.repo_full_name = f"{owner_login}/{repo_name}"
        
        self.branch_name = self.webhook_data.get('ref', '').replace('refs/heads/', '')
        self.commit_list = self.webhook_data.get('commits', [])

    def get_push_commits(self) -> list:
        # 检查是否为 Push 事件
        if self.event_type != 'push':
            logger.warn(f"Invalid event type: {self.event_type}. Only 'push' event is supported now.")
            return []

        # 提取提交信息
        commit_details = []
        for commit in self.commit_list:
            # Gitea 的 commit 格式：author 可能是对象或字符串
            author = commit.get('author', {})
            if isinstance(author, dict):
                author_name = author.get('name', '')
            else:
                author_name = str(author) if author else ''
            
            commit_info = {
                'message': commit.get('message', ''),
                'author': author_name,
                'timestamp': commit.get('timestamp', ''),
                'url': commit.get('url', ''),
            }
            commit_details.append(commit_info)

        logger.info(f"Collected {len(commit_details)} commits from push event.")
        return commit_details

    def add_push_notes(self, message: str):
        # 添加评论到 Gitea Push 请求的提交中（此处假设是在最后一次提交上添加注释）
        if not self.commit_list:
            logger.warn("No commits found to add notes to.")
            return

        # 获取最后一个提交的ID
        last_commit_id = self.commit_list[-1].get('id')
        if not last_commit_id:
            logger.error("Last commit ID not found.")
            return

        # Gitea commit comments API 路径可能需要确认
        # 注意：Gitea 可能不支持在 commit 上直接添加评论
        # 尝试多种可能的路径
        possible_urls = [
            f"api/v1/repos/{self.repo_full_name}/commits/{last_commit_id}/comments",
            f"api/v1/repos/{self.repo_full_name}/git/commits/{last_commit_id}/comments",
            # 某些 Gitea 版本可能使用不同的路径
        ]
        
        headers = {
            'Authorization': f'token {self.gitea_token}',
            'Content-Type': 'application/json'
        }
        data = {
            'body': message
        }
        
        for url_path in possible_urls:
            url = urljoin(f"{self.gitea_url}/", url_path)
            response = requests.post(url, headers=headers, json=data, verify=False)
            logger.debug(f"Add comment to commit {last_commit_id} (trying {url_path}): {response.status_code}, {response.text[:200] if response.text else 'No response'}")
            if response.status_code == 201:
                logger.info("Comment successfully added to push commit.")
                return
            elif response.status_code == 404:
                # 继续尝试下一个路径
                logger.debug(f"Path {url_path} returned 404, trying next...")
                continue
            elif response.status_code == 403:
                # 权限不足，不继续尝试
                logger.error(f"Permission denied when adding comment to commit: {response.status_code}")
                logger.error(response.text[:500] if response.text else 'No response')
                return
            else:
                # 其他错误，记录并返回
                logger.error(f"Failed to add comment: {response.status_code}")
                logger.error(response.text[:500] if response.text else 'No response')
                return
        
        # 所有路径都失败
        logger.warn(f"All commit comment API paths failed for commit {last_commit_id}. "
                   f"Gitea may not support commit comments in this version. "
                   f"Review results will still be saved to database and sent via IM notification.")

    def _get_file_diff(self, filename: str, commit_sha: str, parent_sha: str = None) -> str:
        """
        获取特定文件在某个提交中的 diff
        Gitea 的 compare API 可能不返回 patch，需要单独获取
        :param filename: 文件名
        :param commit_sha: 当前提交 SHA
        :param parent_sha: 父提交 SHA（可选，如果不提供会尝试获取）
        """
        try:
            logger.debug(f"_get_file_diff called for {filename}, commit_sha={commit_sha}, parent_sha={parent_sha}")
            
            # 方法1: 优先尝试使用 commit diff API（最直接、最可靠的方法，不需要 parent_sha）
            # 注意：Gitea API 可能不支持 .diff 扩展名，需要尝试不同的格式
            # 尝试格式1: GET /api/v1/repos/{owner}/{repo}/git/commits/{sha}.diff
            url = urljoin(f"{self.gitea_url}/", f"api/v1/repos/{self.repo_full_name}/git/commits/{commit_sha}.diff")
            headers = {
                'Authorization': f'token {self.gitea_token}'
            }
            response = requests.get(url, headers=headers, verify=False)
            logger.debug(f"Getting diff from git/commits/{commit_sha}.diff API: {response.status_code}, URL: {url}")
            
            # 如果 .diff 格式失败，尝试使用 Accept header 指定格式
            if response.status_code != 200:
                # 尝试格式2: 使用 Accept: text/plain header
                headers['Accept'] = 'text/plain'
                response = requests.get(url, headers=headers, verify=False)
                logger.debug(f"Retrying with Accept: text/plain header: {response.status_code}")
            
            # 如果还是失败，尝试格式3: 使用 patch 参数
            if response.status_code != 200:
                url = urljoin(f"{self.gitea_url}/", f"api/v1/repos/{self.repo_full_name}/git/commits/{commit_sha}")
                params = {'diff': 'true'}
                response = requests.get(url, headers=headers, params=params, verify=False)
                logger.debug(f"Trying with diff=true parameter: {response.status_code}, URL: {url}")
            
            if response.status_code == 200:
                # diff API 返回的是纯文本 diff 格式
                diff_text = response.text
                logger.debug(f"Got diff text from commit diff API, length: {len(diff_text)}, first 500 chars: {diff_text[:500] if diff_text else 'empty'}")
                if diff_text and not diff_text.strip().startswith('{'):
                    # 确保不是 JSON 错误响应
                    # 从完整的 diff 中提取特定文件的部分
                    file_diff = self._extract_file_diff_from_full_diff(diff_text, filename)
                    if file_diff:
                        logger.info(f"✅ Extracted diff for {filename} from commit diff API, length: {len(file_diff)}")
                        return file_diff
                    else:
                        logger.warn(f"Could not extract diff for {filename} from full diff (diff text exists but extraction failed)")
                        # 如果提取失败，尝试直接返回完整 diff（如果只有一个文件或 diff 不太大）
                        if len(diff_text) < 50000:  # 如果 diff 不太大，直接返回
                            logger.debug(f"Returning full diff as fallback for {filename} (extraction failed)")
                            return diff_text
                else:
                    logger.warn(f"Diff API returned empty or invalid text for commit {commit_sha}")
            elif response.status_code == 404:
                logger.warn(f"Commit diff API returned 404 for {commit_sha}, API endpoint may not exist or commit not found")
            else:
                logger.warn(f"Commit diff API returned {response.status_code} for {commit_sha}: {response.text[:200] if response.text else 'No response'}")
            
            # 方法2: 如果 commit diff API 失败，尝试使用 compare API（需要 parent_sha）
            # 如果没有提供 parent_sha，尝试获取
            if not parent_sha:
                logger.debug(f"No parent_sha provided, trying to get it for commit {commit_sha}")
                parent_sha = self.get_parent_commit_id(commit_sha)
                logger.debug(f"Got parent_sha: {parent_sha}")
            
            if parent_sha:
                logger.debug(f"Trying compare API with parent_sha={parent_sha} to get diff for {filename}")
                url = urljoin(f"{self.gitea_url}/", f"api/v1/repos/{self.repo_full_name}/compare/{parent_sha}...{commit_sha}")
                headers = {
                    'Authorization': f'token {self.gitea_token}'
                }
                response = requests.get(url, headers=headers, verify=False)
                logger.debug(f"Getting diff from compare API: {response.status_code}, URL: {url}")
                if response.status_code == 200:
                    compare_data = response.json()
                    # 检查是否有完整的 diff 信息
                    commits = compare_data.get('commits', [])
                    if commits:
                        for commit in commits:
                            commit_files = commit.get('files', [])
                            for file in commit_files:
                                if file.get('filename') == filename:
                                    patch = file.get('patch', '') or file.get('diff', '')
                                    if patch:
                                        logger.debug(f"Got patch for {filename} from compare API, length: {len(patch)}")
                                        return patch
            
            # 方法2: 尝试从 commit 的详细信息中获取（使用 git/commits API）
            url = urljoin(f"{self.gitea_url}/", f"api/v1/repos/{self.repo_full_name}/git/commits/{commit_sha}")
            headers = {
                'Authorization': f'token {self.gitea_token}'
            }
            response = requests.get(url, headers=headers, verify=False)
            logger.debug(f"Getting file diff for {filename} from git/commits API: {response.status_code}")
            if response.status_code == 200:
                commit_data = response.json()
                # 查找文件
                files = commit_data.get('files', [])
                logger.debug(f"Found {len(files)} files in git/commits response, checking for patch field")
                for file in files:
                    if file.get('filename') == filename:
                        patch = file.get('patch', '') or file.get('diff', '')
                        if patch:
                            logger.debug(f"Got patch for {filename} from git/commits API, length: {len(patch)}")
                            return patch
                        else:
                            logger.debug(f"No patch field in file object, file keys: {list(file.keys())}")
            
            # 方法3: 尝试使用 commits API（不是 git/commits）
            url = urljoin(f"{self.gitea_url}/", f"api/v1/repos/{self.repo_full_name}/commits/{commit_sha}")
            response = requests.get(url, headers=headers, verify=False)
            logger.debug(f"Getting file diff for {filename} from commits API: {response.status_code}")
            if response.status_code == 200:
                commit_data = response.json()
                files = commit_data.get('files', [])
                logger.debug(f"Found {len(files)} files in commits response")
                for file in files:
                    if file.get('filename') == filename:
                        patch = file.get('patch', '') or file.get('diff', '')
                        if patch:
                            logger.debug(f"Got patch for {filename} from commits API, length: {len(patch)}")
                            return patch
            
            # 方法4: 尝试获取文件的原始内容并生成 diff
            logger.debug(f"Trying to get file content directly for {filename}")
            if parent_sha:
                # 尝试获取两个版本的文件内容
                old_content = self._get_file_content(filename, parent_sha)
                new_content = self._get_file_content(filename, commit_sha)
                logger.debug(f"Got file contents: old={old_content is not None}, new={new_content is not None}")
                if old_content is not None and new_content is not None:
                    # 生成简单的 diff
                    diff = self._generate_diff(filename, old_content, new_content)
                    if diff:
                        logger.debug(f"Generated diff for {filename} from file contents, length: {len(diff)}")
                        return diff
            
            logger.debug(f"Could not get patch from commit API for {filename} in commit {commit_sha}")
        except Exception as e:
            logger.error(f"Failed to get file diff for {filename}: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
        return ""
    
    def _extract_file_diff_from_full_diff(self, full_diff: str, filename: str) -> str:
        """
        从完整的 diff 文本中提取特定文件的 diff
        """
        try:
            lines = full_diff.split('\n')
            file_diff_lines = []
            in_target_file = False
            
            logger.debug(f"Extracting diff for {filename} from full diff ({len(lines)} lines)")
            
            for i, line in enumerate(lines):
                # 检查是否是目标文件的 diff 开始
                # diff --git a/path/to/file b/path/to/file
                if line.startswith('diff --git'):
                    # 检查是否包含目标文件名（支持 a/ 和 b/ 前缀）
                    # 例如：diff --git a/2.js b/2.js 或 diff --git a/src/2.js b/src/2.js
                    if f"a/{filename}" in line or f"b/{filename}" in line or f"/{filename}" in line:
                        in_target_file = True
                        file_diff_lines.append(line)
                        logger.debug(f"Found diff start for {filename} at line {i}: {line[:100]}")
                    elif in_target_file:
                        # 如果已经在目标文件中，遇到下一个文件的 diff 开始，停止
                        logger.debug(f"Found next file diff at line {i}, stopping extraction")
                        break
                elif in_target_file:
                    # 收集目标文件的所有 diff 行
                    file_diff_lines.append(line)
            
            if file_diff_lines:
                result = '\n'.join(file_diff_lines)
                logger.debug(f"Extracted {len(file_diff_lines)} lines for {filename}, total length: {len(result)}")
                return result
            else:
                logger.warn(f"No diff lines extracted for {filename} from full diff")
        except Exception as e:
            logger.error(f"Failed to extract file diff for {filename}: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
        return ""
    
    def _get_file_content(self, filename: str, commit_sha: str) -> str:
        """
        获取文件在特定提交中的内容
        """
        try:
            # 使用 contents API 获取文件内容
            # URL 编码文件名（处理特殊字符）
            from urllib.parse import quote
            encoded_filename = quote(filename, safe='/')
            url = urljoin(f"{self.gitea_url}/", f"api/v1/repos/{self.repo_full_name}/contents/{encoded_filename}")
            headers = {
                'Authorization': f'token {self.gitea_token}'
            }
            params = {'ref': commit_sha}
            response = requests.get(url, headers=headers, params=params, verify=False)
            logger.debug(f"Getting file content for {filename} at {commit_sha}: {response.status_code}, URL: {url}")
            
            if response.status_code == 200:
                content_data = response.json()
                logger.debug(f"Content data keys: {list(content_data.keys())}")
                
                # Gitea 可能返回 base64 编码的内容
                import base64
                content = content_data.get('content', '')
                if content:
                    # 移除可能的换行符（base64 编码可能包含换行）
                    content = content.replace('\n', '').replace('\r', '')
                    # 解码 base64
                    try:
                        decoded = base64.b64decode(content).decode('utf-8')
                        logger.debug(f"Successfully decoded file content for {filename}, length: {len(decoded)}")
                        return decoded
                    except Exception as e:
                        logger.debug(f"Failed to decode base64 content: {str(e)}")
                        # 如果解码失败，尝试直接返回（可能不是 base64）
                        return content
                else:
                    logger.warn(f"No content field in response for {filename}")
            elif response.status_code == 404:
                logger.debug(f"File {filename} not found at commit {commit_sha} (404)")
            else:
                logger.warn(f"Failed to get file content: {response.status_code}, {response.text[:200]}")
        except Exception as e:
            logger.error(f"Failed to get file content for {filename} at {commit_sha}: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
        return None
    
    def _generate_diff(self, filename: str, old_content: str, new_content: str) -> str:
        """
        生成简单的 unified diff 格式
        """
        try:
            import difflib
            old_lines = old_content.splitlines(keepends=True)
            new_lines = new_content.splitlines(keepends=True)
            
            diff = difflib.unified_diff(
                old_lines,
                new_lines,
                fromfile=f'a/{filename}',
                tofile=f'b/{filename}',
                lineterm=''
            )
            return ''.join(diff)
        except Exception as e:
            logger.debug(f"Failed to generate diff: {str(e)}")
        return ""

    def get_parent_commit_id(self, commit_id: str) -> str:
        # 获取提交的父提交ID
        # 使用 git/commits API（不是 commits API）
        url = urljoin(f"{self.gitea_url}/", f"api/v1/repos/{self.repo_full_name}/git/commits/{commit_id}")
        headers = {
            'Authorization': f'token {self.gitea_token}'
        }
        response = requests.get(url, headers=headers, verify=False)
        logger.debug(
            f"Get commit response from Gitea: {response.status_code}, URL: {url}")

        if response.status_code == 200:
            commit_data = response.json()
            parents = commit_data.get('parents', [])
            if parents:
                parent_sha = parents[0].get('sha', '')
                logger.debug(f"Found parent commit: {parent_sha}")
                return parent_sha
            else:
                logger.debug("No parents found for commit")
        else:
            logger.warn(f"Failed to get parent commit: {response.status_code}")
        return ""

    def repository_compare(self, base: str, head: str):
        """
        比较两个提交之间的差异
        :param base: 基础提交 SHA（before）
        :param head: 目标提交 SHA（after）
        """
        # 比较两个提交之间的差异
        # 尝试使用 {base}...{head} 格式
        url = urljoin(f"{self.gitea_url}/", f"api/v1/repos/{self.repo_full_name}/compare/{base}...{head}")
        headers = {
            'Authorization': f'token {self.gitea_token}'
        }
        response = requests.get(url, headers=headers, verify=False)
        logger.debug(
            f"Get changes response from Gitea for repository_compare: {response.status_code}, {response.text}, URL: {url}")

        if response.status_code == 200:
            # Gitea 返回的格式可能不同，需要转换为统一格式
            compare_data = response.json()
            logger.debug(f"Compare data structure: {list(compare_data.keys())}")
            
            # Gitea compare API 可能返回 files 在 commits 中，或者直接在根级别
            files = compare_data.get('files', [])
            commits = compare_data.get('commits', [])
            
            # 如果没有 files，尝试从 commits 中获取
            if not files and commits:
                # 从最后一个 commit 中获取 files（通常最后一个 commit 包含所有变更）
                last_commit = commits[-1]
                files = last_commit.get('files', [])
                logger.debug(f"Found {len(files)} files in last commit: {[f.get('filename') for f in files]}")
            
            # 如果还是没有 files，尝试从所有 commits 中收集
            if not files and commits:
                # 收集所有 commits 中的 files（去重）
                all_files = {}
                for commit in commits:
                    commit_files = commit.get('files', [])
                    for cf in commit_files:
                        filename = cf.get('filename', '')
                        if filename:
                            # 如果文件已存在，合并信息（保留有更多信息的版本）
                            if filename not in all_files:
                                all_files[filename] = cf
                            else:
                                # 如果新的文件对象有 patch 而旧的没有，替换
                                existing = all_files[filename]
                                if not existing.get('patch') and cf.get('patch'):
                                    all_files[filename] = cf
                                # 合并 stats
                                existing_stats = existing.get('stats', {})
                                cf_stats = cf.get('stats', {})
                                if cf_stats and not existing_stats:
                                    existing['stats'] = cf_stats
                files = list(all_files.values())
                logger.debug(f"Collected {len(files)} unique files from all commits")
            
            # 如果还是没有 files，返回空
            if not files:
                logger.warn("No files found in compare response")
                return []
            
            diffs = []
            logger.debug(f"Processing {len(files)} files, base={base}, head={head}")
            for file in files:
                filename = file.get('filename', '')
                if not filename:
                    continue
                
                logger.debug(f"Processing file: {filename}")
                
                # Gitea 可能不直接返回 patch，需要单独获取
                patch = file.get('patch', '')
                # 如果没有 patch，尝试从其他字段获取
                if not patch:
                    patch = file.get('diff', '')
                
                logger.debug(f"File {filename}: patch from file object: {len(patch) if patch else 0}")
                
                # 如果还是没有 patch，尝试从 commit 的 diff 中获取
                if not patch and commits:
                    logger.debug(f"Trying to get patch from commits for {filename}")
                    # 尝试从 commit 数据中获取
                    for commit in commits:
                        commit_files = commit.get('files', [])
                        for cf in commit_files:
                            if cf.get('filename') == filename:
                                patch = cf.get('patch', '') or cf.get('diff', '')
                                if patch:
                                    logger.debug(f"Found patch in commit data for {filename}, length: {len(patch)}")
                                    break
                        if patch:
                            break
                
                # 如果仍然没有 patch，尝试单独获取文件的 diff
                # 优先使用已有的 base 和 head SHA（最可靠的方法）
                if not patch:
                    logger.debug(f"No patch found yet for {filename}, base={base}, head={head}")
                    if base and head:
                        logger.debug(f"Attempting to get diff for {filename} using base={base}, head={head}")
                        patch = self._get_file_diff(filename, head, parent_sha=base)
                        if patch:
                            logger.info(f"✅ Successfully retrieved patch for {filename} via _get_file_diff with base/head, length: {len(patch)}")
                        else:
                            logger.warn(f"Could not retrieve patch for {filename} using base/head")
                    else:
                        logger.warn(f"Cannot get diff for {filename}: base={base}, head={head} (one or both are missing)")
                
                # 如果还是没有 patch，尝试从最后一个 commit 中获取
                if not patch and commits:
                    last_commit_sha = commits[-1].get('sha', '')
                    if last_commit_sha:
                        # 尝试从 commit 的 parents 中获取
                        commit_parents = commits[-1].get('parents', [])
                        commit_parent_sha = commit_parents[0].get('sha', '') if commit_parents else None
                        if commit_parent_sha:
                            patch = self._get_file_diff(filename, last_commit_sha, parent_sha=commit_parent_sha)
                        else:
                            patch = self._get_file_diff(filename, last_commit_sha)
                
                # 如果还是没有 patch，尝试从 head commit 获取（使用默认的 parent 获取逻辑）
                if not patch and head:
                    logger.debug(f"Attempting to get diff for {filename} from head commit {head} (auto-detect parent)")
                    patch = self._get_file_diff(filename, head)
                    if patch:
                        logger.info(f"Successfully retrieved patch for {filename} via _get_file_diff, length: {len(patch)}")
                    else:
                        logger.warn(f"Could not retrieve patch for {filename} even after trying all methods")
                
                # 从 stats 中获取 additions 和 deletions（如果文件对象中没有）
                additions = file.get('additions', 0)
                deletions = file.get('deletions', 0)
                
                # 如果文件对象中没有，尝试从各种 stats 中获取
                if additions == 0 and deletions == 0:
                    # 方法1: 尝试从文件对象的 stats 中获取
                    stats = file.get('stats', {})
                    if stats:
                        additions = stats.get('additions', 0)
                        deletions = stats.get('deletions', 0)
                    
                    # 方法2: 如果还是没有，尝试从 commit 的 stats 中获取
                    if additions == 0 and deletions == 0 and commits:
                        for commit in commits:
                            commit_files = commit.get('files', [])
                            for cf in commit_files:
                                if cf.get('filename') == filename:
                                    # 先尝试从文件对象的 stats 中获取
                                    cf_stats = cf.get('stats', {})
                                    if cf_stats:
                                        additions = cf_stats.get('additions', 0)
                                        deletions = cf_stats.get('deletions', 0)
                                    # 如果还是没有，尝试从 commit 级别的 stats 中获取
                                    if additions == 0 and deletions == 0:
                                        commit_stats = commit.get('stats', {})
                                        if commit_stats:
                                            # 如果只有一个文件，使用 commit 的 stats
                                            if len(commit_files) == 1:
                                                additions = commit_stats.get('additions', 0)
                                                deletions = commit_stats.get('deletions', 0)
                                            # 如果有多个文件，但当前文件匹配，可以尝试按比例分配（简单处理：使用总数）
                                            # 注意：这不是精确的，但至少能提供一些信息
                                    if additions or deletions:
                                        break
                            if additions or deletions:
                                break
                    
                    # 方法3: 如果还是没有，尝试从 compare 响应的 stats 中获取（根级别）
                    if additions == 0 and deletions == 0:
                        compare_stats = compare_data.get('stats', {})
                        if compare_stats and len(files) == 1:
                            # 如果只有一个文件，直接使用 compare 的 stats
                            additions = compare_stats.get('additions', 0)
                            deletions = compare_stats.get('deletions', 0)
                
                logger.debug(f"File {filename}: additions={additions}, deletions={deletions}, has_patch={bool(patch)}")
                
                diff = {
                    'old_path': filename,
                    'new_path': filename,
                    'diff': patch,
                    'additions': additions,
                    'deletions': deletions,
                }
                # 只要有文件名就添加（即使没有 patch，也可以用于审查）
                diffs.append(diff)
                logger.debug(f"Added file {filename} with patch length: {len(patch) if patch else 0}, additions: {additions}, deletions: {deletions}")
            
            logger.info(f"Extracted {len(diffs)} files from compare response")
            if not diffs:
                logger.warn("No diffs extracted, this might indicate an issue with the API response format")
            return diffs
        elif response.status_code == 404:
            # 如果 {base}...{head} 格式不工作，尝试查询参数格式
            logger.info("Trying query parameter format for compare API")
            url = urljoin(f"{self.gitea_url}/", f"api/v1/repos/{self.repo_full_name}/compare")
            params = {'base': base, 'head': head}
            response = requests.get(url, headers=headers, params=params, verify=False)
            logger.debug(
                f"Get changes response from Gitea (query params): {response.status_code}, {response.text}, URL: {url}")
            if response.status_code == 200:
                compare_data = response.json()
                logger.debug(f"Compare data structure (query params): {list(compare_data.keys())}")
                
                # Gitea compare API 可能返回 files 在 commits 中，或者直接在根级别
                files = compare_data.get('files', [])
                # 如果没有 files，尝试从 commits 中获取
                if not files:
                    commits = compare_data.get('commits', [])
                    if commits:
                        # 从最后一个 commit 中获取 files
                        last_commit = commits[-1]
                        files = last_commit.get('files', [])
                        logger.debug(f"Found {len(files)} files in last commit (query params)")
                
                if not files:
                    logger.warn("No files found in compare response (query params)")
                    return []
                
                diffs = []
                for file in files:
                    filename = file.get('filename', '')
                    if not filename:
                        continue
                    
                    patch = file.get('patch', '') or file.get('diff', '')
                    # 如果还是没有 patch，尝试单独获取
                    if not patch and head:
                        patch = self._get_file_diff(filename, head)
                    
                    additions = file.get('additions', 0)
                    deletions = file.get('deletions', 0)
                    if additions == 0 and deletions == 0:
                        stats = file.get('stats', {})
                        if stats:
                            additions = stats.get('additions', 0)
                            deletions = stats.get('deletions', 0)
                    
                    diff = {
                        'old_path': filename,
                        'new_path': filename,
                        'diff': patch,
                        'additions': additions,
                        'deletions': deletions,
                    }
                    diffs.append(diff)
                    logger.debug(f"Added file {filename} with patch length: {len(patch) if patch else 0}")
                
                logger.info(f"Extracted {len(diffs)} files from compare response (query params)")
                return diffs
        else:
            logger.warn(
                f"Failed to get changes for repository_compare: {response.status_code}, {response.text}")
            return []

    def get_push_changes(self) -> list:
        # 检查是否为 Push 事件
        if self.event_type != 'push':
            logger.warn(f"Invalid event type: {self.event_type}. Only 'push' event is supported now.")
            return []

        # 如果没有提交，返回空列表
        if not self.commit_list:
            logger.info("No commits found in push event.")
            return []

        # 检查是否为 Tag 推送
        ref = self.webhook_data.get('ref', '')
        if ref.startswith('refs/tags/'):
            logger.info(f"Tag push event detected: {ref}, skipping.")
            return []

        # 优先尝试compare API获取变更
        before = self.webhook_data.get('before', '')
        after = self.webhook_data.get('after', '')
        if before and after:
            # 删除分支处理
            if after.startswith('0000000'):
                logger.info("Branch deletion detected, skipping.")
                return []
            
            # 创建分支处理
            if before.startswith('0000000'):
                logger.info("Branch creation detected, getting parent commit.")
                first_commit_id = self.commit_list[0].get('id')
                if first_commit_id:
                    parent_commit_id = self.get_parent_commit_id(first_commit_id)
                    if parent_commit_id:
                        before = parent_commit_id
                    else:
                        logger.warn("Could not get parent commit for new branch.")
                        return []
            
            changes = self.repository_compare(before, after)
            if not changes:
                logger.info("No changes found in push event after repository_compare.")
                # 即使没有 changes，也记录一下，方便调试
                logger.debug(f"Before: {before}, After: {after}, Commits: {len(self.commit_list)}")
            else:
                logger.info(f"Found {len(changes)} file changes in push event")
            return changes
        else:
            logger.warn("before or after not found in webhook data.")
            return []

    def create_or_get_review_issue(self, review_metadata: dict) -> int:
        """
        为 Push 事件创建或获取审核 Issue
        :param review_metadata: 包含 repo, branch, commit, author 等信息的字典
        :return: Issue 编号
        """
        if not self.repo_full_name:
            logger.error("repo_full_name is empty, cannot create issue")
            raise ValueError("repo_full_name is required")
        
        if not self.commit_list:
            logger.error("commit_list is empty, cannot create issue")
            raise ValueError("commit_list is required")
        
        # 构建 Issue 标题：使用 commit SHA 的前 7 位
        commit_sha = review_metadata.get('commit_sha', '')
        if not commit_sha and self.commit_list:
            commit_sha = self.commit_list[-1].get('id', '')
        commit_short = commit_sha[:7] if commit_sha else 'unknown'
        branch_name = self.branch_name or 'unknown'
        issue_title = f"[AI Review] {self.repo_full_name}@{branch_name}:{commit_short}"
        
        # 查询是否已存在 Issue
        existing_issue = self._find_existing_issue(issue_title)
        if existing_issue:
            logger.info(f"Found existing issue #{existing_issue['number']} for commit {commit_short}")
            return existing_issue['number']
        
        # 创建新 Issue
        issue_body = self._build_push_issue_body(review_metadata)
        issue_number = self._create_issue(issue_title, issue_body)
        
        logger.info(f"Created new issue #{issue_number} for commit {commit_short}")
        return issue_number

    def add_issue_comment(self, issue_number: int, review_result: str):
        """
        在 Issue 中添加审核评论
        :param issue_number: Issue 编号
        :param review_result: 审核结果文本
        """
        if not self.repo_full_name:
            logger.error("repo_full_name is empty, cannot add comment")
            return
        
        if not issue_number:
            logger.error("issue_number is empty, cannot add comment")
            return
        
        if not review_result:
            logger.warn("review_result is empty, skipping comment")
            return
        
        url = urljoin(f"{self.gitea_url}/", 
                      f"api/v1/repos/{self.repo_full_name}/issues/{issue_number}/comments")
        
        headers = {
            'Authorization': f'token {self.gitea_token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'body': f"## AI Code Review Result\n\n{review_result}"
        }
        
        logger.info(f"Attempting to add comment to issue #{issue_number} in {self.repo_full_name}")
        
        try:
            response = requests.post(url, headers=headers, json=data, verify=False, timeout=30)
            if response.status_code == 201:
                logger.info(f"✅ Comment successfully added to issue #{issue_number}")
            else:
                logger.error(f"❌ Failed to add comment to issue #{issue_number}: {response.status_code}")
                logger.error(f"Response: {response.text[:500] if response.text else 'No response'}")
        except Exception as e:
            logger.error(f"Exception when adding comment to issue: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())

    def _find_existing_issue(self, title_pattern: str) -> dict:
        """
        查找已存在的 Issue
        :param title_pattern: 标题模式（用于搜索）
        :return: Issue 信息字典，如果不存在返回 None
        """
        if not self.repo_full_name:
            return None
        
        url = urljoin(f"{self.gitea_url}/", 
                      f"api/v1/repos/{self.repo_full_name}/issues")
        
        headers = {
            'Authorization': f'token {self.gitea_token}',
            'Content-Type': 'application/json'
        }
        
        params = {
            'state': 'all',
            'page': 1,
            'limit': 100
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, verify=False, timeout=30)
            if response.status_code == 200:
                issues = response.json()
                for issue in issues:
                    if issue.get('title') == title_pattern:
                        logger.debug(f"Found matching issue: #{issue.get('number')} - {issue.get('title')}")
                        return issue
            else:
                logger.warn(f"Failed to search issues: {response.status_code}")
            return None
        except Exception as e:
            logger.error(f"Exception when searching for issue: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
            return None

    def _get_label_id(self, label_name: str) -> int:
        """
        通过标签名称获取标签 ID
        :param label_name: 标签名称
        :return: 标签 ID，如果不存在返回 None
        """
        if not self.repo_full_name:
            return None
        
        url = urljoin(f"{self.gitea_url}/", 
                      f"api/v1/repos/{self.repo_full_name}/labels")
        
        headers = {
            'Authorization': f'token {self.gitea_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(url, headers=headers, verify=False, timeout=30)
            if response.status_code == 200:
                labels = response.json()
                for label in labels:
                    if label.get('name') == label_name:
                        return label.get('id')
            return None
        except Exception as e:
            logger.error(f"Error getting label ID: {str(e)}")
            return None

    def _create_issue(self, title: str, body: str) -> int:
        """
        创建新 Issue
        :param title: Issue 标题
        :param body: Issue 内容
        :return: Issue 编号
        """
        if not self.repo_full_name:
            raise ValueError("repo_full_name is required")
        
        url = urljoin(f"{self.gitea_url}/", 
                      f"api/v1/repos/{self.repo_full_name}/issues")
        
        headers = {
            'Authorization': f'token {self.gitea_token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'title': title,
            'body': body,
            'state': 'open'
        }
        
        issue_labels = os.getenv('GITEA_REVIEW_ISSUE_LABELS', '')
        if issue_labels:
            labels = [label.strip() for label in issue_labels.split(',')]
            # 过滤空标签
            labels = [label for label in labels if label]
            if labels:
                # 尝试将标签转换为整数（ID），如果失败则跳过
                try:
                    # 尝试获取标签 ID
                    label_ids = []
                    for label in labels:
                        # 检查是否为数字
                        if label.isdigit():
                            label_ids.append(int(label))
                        else:
                            # 如果是字符串，尝试通过名称获取 ID
                            label_id = self._get_label_id(label)
                            if label_id:
                                label_ids.append(label_id)
                    
                    if label_ids:
                        data['labels'] = label_ids
                except Exception as e:
                    logger.error(f"Error processing labels: {str(e)}")
                    # 如果处理标签失败，跳过添加标签
                    pass
        
        try:
            response = requests.post(url, headers=headers, json=data, verify=False, timeout=30)
            if response.status_code == 201:
                issue = response.json()
                issue_number = issue.get('number')
                logger.info(f"Successfully created issue #{issue_number}")
                return issue_number
            else:
                error_msg = f"Failed to create issue: {response.status_code}"
                logger.error(error_msg)
                logger.error(f"Response: {response.text[:500] if response.text else 'No response'}")
                raise Exception(error_msg)
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception when creating issue: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Exception when creating issue: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
            raise

    def _build_push_issue_body(self, metadata: dict) -> str:
        """
        构建 Push 事件的 Issue Body
        """
        commit_sha = metadata.get('commit_sha', '')
        if not commit_sha and self.commit_list:
            commit_sha = self.commit_list[-1].get('id', 'N/A')
        
        body_lines = [
            "## AI Code Review",
            "",
            f"**Repository**: {self.repo_full_name}",
            f"**Branch**: {self.branch_name}",
            f"**Commit**: {commit_sha}",
            f"**Author**: {metadata.get('author', 'N/A')}",
            f"**Review Time**: {metadata.get('review_time', 'N/A')}",
            f"**Files Changed**: {metadata.get('file_count', 0)}",
            f"**Additions**: +{metadata.get('additions', 0)}",
            f"**Deletions**: -{metadata.get('deletions', 0)}",
            ""
        ]
        
        if metadata.get('files'):
            body_lines.append("### Changed Files")
            body_lines.append("")
            for file in metadata['files']:
                body_lines.append(f"- `{file}`")
            body_lines.append("")
        
        body_lines.append("---")
        body_lines.append("*This issue is automatically created for AI code review tracking.*")
        
        return "\n".join(body_lines)


class PullRequestHandler:
    def __init__(self, webhook_data: dict, gitea_token: str, gitea_url: str):
        self.pull_request_number = None
        self.webhook_data = webhook_data
        self.gitea_token = gitea_token
        self.gitea_url = gitea_url
        self.event_type = None
        self.repo_full_name = None
        self.action = None
        self.parse_event_type()

    def parse_event_type(self):
        # 提取 event_type
        self.event_type = 'pull_request'  # Gitea webhook 的事件类型通过 header 中的 X-Gitea-Event 获取，API 中已处理
        self.parse_pull_request_event()

    def parse_pull_request_event(self):
        # 提取 Pull Request 的相关参数
        pull_request = self.webhook_data.get('pull_request', {})
        self.pull_request_number = pull_request.get('number')
        
        # 优先使用 pull_request.base.repo.full_name，如果没有则使用 repository.full_name
        base_repo = pull_request.get('base', {}).get('repo', {})
        self.repo_full_name = base_repo.get('full_name')
        if not self.repo_full_name:
            repository = self.webhook_data.get('repository', {})
            self.repo_full_name = repository.get('full_name')
            if not self.repo_full_name:
                # 降级方案
                owner = repository.get('owner', {})
                owner_login = owner.get('login', '')
                repo_name = repository.get('name', '')
                if owner_login and repo_name:
                    self.repo_full_name = f"{owner_login}/{repo_name}"
        
        self.action = self.webhook_data.get('action')
        
        # 添加调试日志
        logger.debug(f"Parsed PR event: number={self.pull_request_number}, repo={self.repo_full_name}, action={self.action}")
        if not self.pull_request_number:
            logger.warn("pull_request_number is None or missing in webhook data")
        if not self.repo_full_name:
            logger.warn("repo_full_name is None or missing in webhook data")

    def get_pull_request_changes(self) -> list:
        # 检查是否为 Pull Request Hook 事件
        if self.event_type != 'pull_request':
            logger.warn(f"Invalid event type: {self.event_type}. Only 'pull_request' event is supported now.")
            return []

        # Gitea pull request changes API可能存在延迟，多次尝试
        max_retries = 3  # 最大重试次数
        retry_delay = 10  # 重试间隔时间（秒）
        for attempt in range(max_retries):
            # 调用 Gitea API 获取 Pull Request 的 files（变更）
            url = urljoin(f"{self.gitea_url}/", f"api/v1/repos/{self.repo_full_name}/pulls/{self.pull_request_number}/files")
            headers = {
                'Authorization': f'token {self.gitea_token}',
                'Content-Type': 'application/json'
            }
            response = requests.get(url, headers=headers, verify=False)
            logger.debug(
                f"Get changes response from Gitea (attempt {attempt + 1}): {response.status_code}, {response.text}, URL: {url}")

            # 检查请求是否成功
            if response.status_code == 200:
                files = response.json()
                if files:
                    # 获取 PR 的 base 和 head 信息用于获取 diff
                    pull_request = self.webhook_data.get('pull_request', {})
                    base = pull_request.get('base', {})
                    head = pull_request.get('head', {})
                    base_sha = base.get('sha', '')
                    head_sha = head.get('sha', '')
                    
                    # 转换成统一格式的changes
                    changes = []
                    for file in files:
                        filename = file.get('filename', '')
                        patch = file.get('patch', '')
                        
                        # 如果 patch 为空，尝试从 compare API 获取
                        if not patch and base_sha and head_sha:
                            logger.debug(f"No patch in file object for {filename}, trying to get from compare API")
                            patch = self._get_file_diff_from_pr(filename, base_sha, head_sha)
                        
                        change = {
                            'old_path': filename,
                            'new_path': filename,
                            'diff': patch,
                            'additions': file.get('additions', 0),
                            'deletions': file.get('deletions', 0)
                        }
                        changes.append(change)
                    return changes
                else:
                    logger.info(
                        f"Changes is empty, retrying in {retry_delay} seconds... (attempt {attempt + 1}/{max_retries}), URL: {url}")
                    time.sleep(retry_delay)
            else:
                logger.warn(f"Failed to get changes from Gitea (URL: {url}): {response.status_code}, {response.text}")
                return []

        logger.warning(f"Max retries ({max_retries}) reached. Changes is still empty.")
        return []  # 达到最大重试次数后返回空列表

    def _get_file_diff_from_pr(self, filename: str, base_sha: str, head_sha: str) -> str:
        """
        从 PR 的 base 和 head 获取特定文件的 diff
        :param filename: 文件名
        :param base_sha: base 分支的 SHA
        :param head_sha: head 分支的 SHA
        :return: diff 内容
        """
        try:
            # 使用 compare API 获取 diff
            url = urljoin(f"{self.gitea_url}/", 
                          f"api/v1/repos/{self.repo_full_name}/compare/{base_sha}...{head_sha}")
            headers = {
                'Authorization': f'token {self.gitea_token}'
            }
            response = requests.get(url, headers=headers, verify=False, timeout=30)
            
            if response.status_code == 200:
                compare_data = response.json()
                commits = compare_data.get('commits', [])
                
                # 从 commits 中查找文件
                for commit in commits:
                    commit_files = commit.get('files', [])
                    for file in commit_files:
                        if file.get('filename') == filename:
                            patch = file.get('patch', '') or file.get('diff', '')
                            if patch:
                                logger.debug(f"Got patch for {filename} from compare API, length: {len(patch)}")
                                return patch
                
                # 如果从 commits 中没找到，尝试从根级别的 files 中获取
                files = compare_data.get('files', [])
                for file in files:
                    if file.get('filename') == filename:
                        patch = file.get('patch', '') or file.get('diff', '')
                        if patch:
                            logger.debug(f"Got patch for {filename} from compare API files, length: {len(patch)}")
                            return patch
                
                # 如果还是没有，尝试使用 commit diff API
                logger.debug(f"Trying commit diff API for {filename}")
                diff_url = urljoin(f"{self.gitea_url}/", 
                                   f"api/v1/repos/{self.repo_full_name}/git/commits/{head_sha}.diff")
                diff_response = requests.get(diff_url, headers=headers, verify=False, timeout=30)
                if diff_response.status_code == 200:
                    full_diff = diff_response.text
                    # 提取特定文件的 diff
                    from src.gitea.webhook_handler import PushHandler
                    # 创建一个临时的 PushHandler 实例来使用 _extract_file_diff_from_full_diff 方法
                    # 或者直接在这里实现提取逻辑
                    file_diff = self._extract_file_diff_from_full_diff(full_diff, filename)
                    if file_diff:
                        logger.debug(f"Extracted diff for {filename} from commit diff, length: {len(file_diff)}")
                        return file_diff
            else:
                logger.warn(f"Compare API returned {response.status_code} for {filename}")
        except Exception as e:
            logger.error(f"Exception when getting file diff for {filename}: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
        return ""

    def _extract_file_diff_from_full_diff(self, full_diff: str, filename: str) -> str:
        """
        从完整的 diff 文本中提取特定文件的 diff
        """
        try:
            lines = full_diff.split('\n')
            file_diff_lines = []
            in_target_file = False
            
            for i, line in enumerate(lines):
                # 检查是否是目标文件的 diff 开始
                if line.startswith('diff --git'):
                    # 检查是否包含目标文件名
                    if f"a/{filename}" in line or f"b/{filename}" in line or f"/{filename}" in line:
                        in_target_file = True
                        file_diff_lines.append(line)
                    elif in_target_file:
                        # 如果已经在目标文件中，遇到下一个文件的 diff 开始，停止
                        break
                elif in_target_file:
                    # 收集目标文件的所有 diff 行
                    file_diff_lines.append(line)
            
            if file_diff_lines:
                result = '\n'.join(file_diff_lines)
                logger.debug(f"Extracted {len(file_diff_lines)} lines for {filename}")
                return result
        except Exception as e:
            logger.error(f"Failed to extract file diff for {filename}: {str(e)}")
        return ""

    def get_pull_request_commits(self) -> list:
        # 检查是否为 Pull Request Hook 事件
        if self.event_type != 'pull_request':
            return []

        # 调用 Gitea API 获取 Pull Request 的 commits
        url = urljoin(f"{self.gitea_url}/", f"api/v1/repos/{self.repo_full_name}/pulls/{self.pull_request_number}/commits")
        headers = {
            'Authorization': f'token {self.gitea_token}',
            'Content-Type': 'application/json'
        }
        response = requests.get(url, headers=headers, verify=False)
        logger.debug(f"Get commits response from Gitea: {response.status_code}, {response.text}")
        
        # 检查请求是否成功
        if response.status_code == 200:
            # 将Gitea的commits转换为统一格式的commits
            gitea_commits = response.json()
            unified_commits = []
            for commit in gitea_commits:
                # Gitea commit 格式可能不同，需要转换
                commit_data = commit.get('commit', commit)  # 有些API返回commit字段，有些直接返回
                author = commit_data.get('author', {})
                if isinstance(author, dict):
                    author_name = author.get('name', '')
                else:
                    author_name = str(author) if author else ''
                
                unified_commit = {
                    'id': commit.get('sha', commit.get('id', '')),
                    'title': commit_data.get('message', '').split('\n')[0],
                    'message': commit_data.get('message', ''),
                    'author_name': author_name,
                    'author_email': commit_data.get('author', {}).get('email', '') if isinstance(commit_data.get('author'), dict) else '',
                    'created_at': commit_data.get('timestamp', ''),
                    'web_url': commit.get('html_url', '')
                }
                unified_commits.append(unified_commit)
            return unified_commits
        else:
            logger.warn(f"Failed to get commits: {response.status_code}, {response.text}")
            return []

    def add_pull_request_notes(self, review_result):
        """
        添加评论到 Gitea Pull Request
        :param review_result: 审核结果文本
        """
        if not self.repo_full_name:
            logger.error("repo_full_name is empty, cannot add comment")
            return
        
        if not self.pull_request_number:
            logger.error("pull_request_number is empty, cannot add comment")
            return
        
        if not review_result:
            logger.warn("review_result is empty, skipping comment")
            return
        
        headers = {
            'Authorization': f'token {self.gitea_token}',
            'Content-Type': 'application/json'
        }
        data = {
            'body': review_result
        }
        
        logger.info(f"Attempting to add comment to Gitea PR #{self.pull_request_number} in {self.repo_full_name}")
        logger.debug(f"Comment length: {len(review_result)} characters")
        
        # 尝试多个可能的 API 端点（Gitea 不同版本可能使用不同的端点）
        possible_urls = [
            f"api/v1/repos/{self.repo_full_name}/issues/{self.pull_request_number}/comments",
            f"api/v1/repos/{self.repo_full_name}/pulls/{self.pull_request_number}/comments",
        ]
        
        for url_path in possible_urls:
            url = urljoin(f"{self.gitea_url}/", url_path)
            logger.debug(f"Trying API endpoint: {url}")
            
            try:
                response = requests.post(url, headers=headers, json=data, verify=False, timeout=30)
                logger.info(f"Add comment to Gitea PR {url}: status_code={response.status_code}")
                
                if response.status_code == 201:
                    logger.info("✅ Comment successfully added to pull request.")
                    return
                elif response.status_code == 404:
                    # 404 可能表示端点不存在，尝试下一个
                    logger.debug(f"Endpoint {url_path} returned 404, trying next endpoint...")
                    continue
                else:
                    logger.error(f"❌ Failed to add comment: status_code={response.status_code}")
                    logger.error(f"Response text: {response.text[:500] if response.text else 'No response text'}")
                    
                    # 尝试提供更详细的错误信息
                    if response.status_code == 403:
                        logger.error("403 Forbidden - Check if token has write permissions to the repository")
                        # 权限问题，不继续尝试其他端点
                        return
                    elif response.status_code == 401:
                        logger.error("401 Unauthorized - Check if token is valid")
                        # 认证问题，不继续尝试其他端点
                        return
                    else:
                        # 其他错误，尝试下一个端点
                        logger.debug(f"Error {response.status_code} with endpoint {url_path}, trying next...")
                        continue
            except requests.exceptions.RequestException as e:
                logger.error(f"Request exception when adding comment to {url_path}: {str(e)}")
                # 网络错误，尝试下一个端点
                continue
        
        # 所有端点都失败了
        logger.error(f"❌ All API endpoints failed. Could not add comment to PR #{self.pull_request_number}")
        import traceback
        logger.debug(traceback.format_exc())

    def create_or_get_review_issue(self, review_metadata: dict) -> int:
        """
        创建或获取审核 Issue
        :param review_metadata: 包含 repo, branch, commit, author 等信息的字典
        :return: Issue 编号
        """
        if not self.repo_full_name:
            logger.error("repo_full_name is empty, cannot create issue")
            raise ValueError("repo_full_name is required")
        
        if not self.pull_request_number:
            logger.error("pull_request_number is empty, cannot create issue")
            raise ValueError("pull_request_number is required")
        
        # 1. 构建 Issue 标题
        issue_title = f"[AI Review] PR #{self.pull_request_number}"
        
        # 2. 查询是否已存在 Issue
        existing_issue = self._find_existing_issue(issue_title)
        if existing_issue:
            logger.info(f"Found existing issue #{existing_issue['number']} for PR #{self.pull_request_number}")
            return existing_issue['number']
        
        # 3. 创建新 Issue
        issue_body = self._build_issue_body(review_metadata)
        issue_number = self._create_issue(issue_title, issue_body)
        
        logger.info(f"Created new issue #{issue_number} for PR #{self.pull_request_number}")
        return issue_number

    def add_issue_comment(self, issue_number: int, review_result: str):
        """
        在 Issue 中添加审核评论
        :param issue_number: Issue 编号
        :param review_result: 审核结果文本
        """
        if not self.repo_full_name:
            logger.error("repo_full_name is empty, cannot add comment")
            return
        
        if not issue_number:
            logger.error("issue_number is empty, cannot add comment")
            return
        
        if not review_result:
            logger.warn("review_result is empty, skipping comment")
            return
        
        url = urljoin(f"{self.gitea_url}/", 
                      f"api/v1/repos/{self.repo_full_name}/issues/{issue_number}/comments")
        
        headers = {
            'Authorization': f'token {self.gitea_token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'body': f"## AI Code Review Result\n\n{review_result}"
        }
        
        logger.info(f"Attempting to add comment to issue #{issue_number} in {self.repo_full_name}")
        
        try:
            response = requests.post(url, headers=headers, json=data, verify=False, timeout=30)
            if response.status_code == 201:
                logger.info(f"✅ Comment successfully added to issue #{issue_number}")
            else:
                logger.error(f"❌ Failed to add comment to issue #{issue_number}: {response.status_code}")
                logger.error(f"Response: {response.text[:500] if response.text else 'No response'}")
        except Exception as e:
            logger.error(f"Exception when adding comment to issue: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())

    def _find_existing_issue(self, title_pattern: str) -> dict:
        """
        查找已存在的 Issue
        :param title_pattern: 标题模式（用于搜索）
        :return: Issue 信息字典，如果不存在返回 None
        """
        if not self.repo_full_name:
            return None
        
        # 使用 Gitea 的 Issue 列表 API
        url = urljoin(f"{self.gitea_url}/", 
                      f"api/v1/repos/{self.repo_full_name}/issues")
        
        headers = {
            'Authorization': f'token {self.gitea_token}',
            'Content-Type': 'application/json'
        }
        
        params = {
            'state': 'all',  # 包括已关闭的 Issue
            'page': 1,
            'limit': 100
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, verify=False, timeout=30)
            if response.status_code == 200:
                issues = response.json()
                # 精确匹配标题
                for issue in issues:
                    if issue.get('title') == title_pattern:
                        logger.debug(f"Found matching issue: #{issue.get('number')} - {issue.get('title')}")
                        return issue
            else:
                logger.warn(f"Failed to search issues: {response.status_code}")
            return None
        except Exception as e:
            logger.error(f"Exception when searching for issue: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
            return None

    def _create_issue(self, title: str, body: str) -> int:
        """
        创建新 Issue
        :param title: Issue 标题
        :param body: Issue 内容
        :return: Issue 编号
        """
        if not self.repo_full_name:
            raise ValueError("repo_full_name is required")
        
        url = urljoin(f"{self.gitea_url}/", 
                      f"api/v1/repos/{self.repo_full_name}/issues")
        
        headers = {
            'Authorization': f'token {self.gitea_token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'title': title,
            'body': body,
            'state': 'open'
        }
        
        # 检查是否有配置的标签
        issue_labels = os.getenv('GITEA_REVIEW_ISSUE_LABELS', '')
        if issue_labels:
            # 注意：Gitea API 需要标签 ID 或名称，这里使用名称
            labels = [label.strip() for label in issue_labels.split(',')]
            data['labels'] = labels
        
        try:
            response = requests.post(url, headers=headers, json=data, verify=False, timeout=30)
            if response.status_code == 201:
                issue = response.json()
                issue_number = issue.get('number')
                logger.info(f"Successfully created issue #{issue_number}")
                return issue_number
            else:
                error_msg = f"Failed to create issue: {response.status_code}"
                logger.error(error_msg)
                logger.error(f"Response: {response.text[:500] if response.text else 'No response'}")
                raise Exception(error_msg)
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception when creating issue: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Exception when creating issue: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
            raise

    def _build_issue_body(self, metadata: dict) -> str:
        """
        构建 Issue Body 内容
        :param metadata: 元数据字典
        :return: Markdown 格式的 Issue Body
        """
        pull_request = self.webhook_data.get('pull_request', {})
        base = pull_request.get('base', {})
        head = pull_request.get('head', {})
        
        body_lines = [
            "## AI Code Review",
            "",
            f"**Repository**: {self.repo_full_name}",
            f"**Pull Request**: #{self.pull_request_number}",
            f"**Source Branch**: {head.get('ref', 'N/A')}",
            f"**Target Branch**: {base.get('ref', 'N/A')}",
            f"**Author**: {metadata.get('author', 'N/A')}",
            f"**Review Time**: {metadata.get('review_time', 'N/A')}",
            f"**Files Changed**: {metadata.get('file_count', 0)}",
            f"**Additions**: +{metadata.get('additions', 0)}",
            f"**Deletions**: -{metadata.get('deletions', 0)}",
            ""
        ]
        
        if metadata.get('files'):
            body_lines.append("### Changed Files")
            body_lines.append("")
            for file in metadata['files']:
                body_lines.append(f"- `{file}`")
            body_lines.append("")
        
        body_lines.append("---")
        body_lines.append("*This issue is automatically created for AI code review tracking.*")
        
        return "\n".join(body_lines)

    def target_branch_protected(self) -> bool:
        # 获取受保护的分支列表
        url = urljoin(f"{self.gitea_url}/", f"api/v1/repos/{self.repo_full_name}/branches")
        params = {'protected': 'true'}
        headers = {
            'Authorization': f'token {self.gitea_token}',
            'Content-Type': 'application/json'
        }

        response = requests.get(url, headers=headers, params=params, verify=False)
        if response.status_code == 200:
            data = response.json()
            pull_request = self.webhook_data.get('pull_request', {})
            target_branch = pull_request.get('base', {}).get('ref', '')
            # 遍历受保护分支列表，使用 fnmatch 匹配（支持通配符）
            return any(fnmatch.fnmatch(target_branch, item.get('name', '')) for item in data)
        else:
            logger.warn(f"Failed to get protected branches: {response.status_code}, {response.text}")
            return False

