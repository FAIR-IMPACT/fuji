# SPDX-FileCopyrightText: 2020 PANGAEA (https://www.pangaea.de/)
#
# SPDX-License-Identifier: MIT

import json
import os
import re
from configparser import ConfigParser

from github import Auth, Github
from github.GithubException import UnknownObjectException


class GithubHarvester:
    def __init__(self, id, logger, host="https://github.com"):
        # Read Github API access token from config file.
        config = ConfigParser()
        config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), "../config/github.ini"))
        token = config["ACCESS"]["token"]
        if token != "":
            auth = Auth.Token(token)
        else:  # empty token, so no authentication possible (rate limit will be much lower)
            auth = None
            print("Running in unauthenticated mode. Capabilities are limited.")
            self.logger.warning(
                "FRSM-09-A1 : Running in unauthenticated mode. Capabilities are limited."
            )  # TODO: would be better if it were a general warning!
        self.id = id
        self.host = host
        if host != "https://github.com":
            base_url = f"{self.host}/api/v3"
            self.handle = Github(auth=auth, base_url=base_url)
        else:
            self.handle = Github(auth=auth)
        self.logger = logger
        self.data = {}  # dictionary with all info
        fuji_server_dir = os.path.dirname(os.path.dirname(__file__))  # project_root
        software_file_path = os.path.join(fuji_server_dir, "data", "software_file.json")
        with open(software_file_path) as f:
            self.files_map = json.load(f)

    def harvest(self):
        # check if it's a URL or repo ID
        # NOTE: this should probably be handled by IdentifierHelper, but I don't understand that module yet.
        if self.id.count("/") > 1:  # URL
            self.url = self.id
            _, self.username, self.repo_name = self.id.rsplit("/", 2)
        else:  # repo ID
            self.username, self.repo_name = self.id.split("/")
            self.url = "/".join([self.endpoint, self.username, self.repo_name])
        self.repo_id = "/".join([self.username, self.repo_name])

        # access repo via GitHub API
        try:
            repo = self.handle.get_repo(self.repo_id)
        except UnknownObjectException:
            print("Could not find repo.")
            self.logger.warning(
                "FRSM-09-A1 : Could not find repository on GitHub."
            )  # TODO: would be better if it were a general warning!
            return

        # harvesting
        try:  # LICENSE
            license_file = repo.get_license()
            self.data["license_path"] = license_file.path
            self.data["license"] = license_file.license.name
        except UnknownObjectException:
            pass

        # identify source code (sample files in the main language used in the repo)
        repo_languages = repo.get_languages()
        if repo_languages != {}:
            self.data["languages"] = repo_languages
        main_source_code_language = repo.language
        if main_source_code_language is not None:
            self.data["main_language"] = main_source_code_language
            query = f" repo:{self.repo_id} language:{main_source_code_language}"  # needs the space in front as every query needs a string to match on
            source_code_files = self.handle.search_code(query)
            # extract code of up to n=5 files
            n = min(5, source_code_files.totalCount)
            source_code_samples = []
            for i in range(n):
                source_code_samples.append(
                    {
                        "path": source_code_files[i].path,
                        "language": main_source_code_language,
                        "content": source_code_files[i].decoded_content,
                    }
                )
            if len(source_code_samples) > 0:
                self.data["source_code_samples"] = source_code_samples

        self.retrieve_all(repo)

    def retrieve_all(self, repo):
        file_pattern = r"|".join([rf"(?P<{k}>{'|'.join(v['pattern'])})" for k, v in self.files_map.items()])
        repo_contents = repo.get_contents("")
        while repo_contents:
            content_file = repo_contents.pop(0)
            if content_file.type == "dir":
                repo_contents.extend(repo.get_contents(content_file.path))
            else:
                m = re.fullmatch(file_pattern, content_file.path)
                if m is not None and any(m.groupdict().values()):
                    for k, v in m.groupdict().items():
                        if v is not None:
                            if self.files_map[k]["parse"] == "full":
                                file_entry = {
                                    "name": content_file.name,
                                    "path": content_file.path,
                                    "content": content_file.decoded_content,
                                }
                            elif self.files_map[k]["parse"] == "file_name":
                                file_entry = {"name": content_file.name, "path": content_file.path}
                            else:
                                self.logger.warning(
                                    f"FRSM-09-A1 : Parsing strategy {self.files_map[k]['parse']} is currently not implemented. Choose one of 'full' or 'file_name' for files {k}. Defaulting to parsing strategy 'file_name'."
                                )
                                file_entry = {"name": content_file.name, "path": content_file.path}
                            try:
                                self.data[k].append(file_entry)
                            except KeyError:
                                self.data[k] = [file_entry]
