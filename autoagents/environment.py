#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
import re
import json
import datetime
import websockets
from common import MessageType, format_message, timestamp
from typing import Iterable

from pydantic import BaseModel, Field

from autoagents.memory import Memory
from autoagents.roles import Role
from autoagents.schema import Message
from autoagents.actions import Requirement
from autoagents.roles import CustomRole, ActionObserver

class Environment(BaseModel):
    """环境，承载一批角色，角色可以向环境发布消息，可以被其他角色观察到"""

    roles: dict[str, Role] = Field(default_factory=dict)
    memory: Memory = Field(default_factory=Memory)
    history: str = Field(default='')
    new_roles_args: dict = Field(default_factory=dict)
    new_roles: dict[str, Role] = Field(default_factory=dict)
    steps: list = Field(default_factory=list)
    msg_json: list = Field(default_factory=list)
    json_log: str = Field(default='./logs/json_log.json')
    task_id: str = Field(default='')
    proxy: str = Field(default='')
    llm_api_key: str = Field(default='')
    serpapi_key: str = Field(default='')
    alg_msg_queue: object = Field(default=None)
    mock_mode: bool = Field(default=False)
    _content_cache: dict = {}

    class Config:
        arbitrary_types_allowed = True


    def add_role(self, role: Role):
        """增加一个在当前环境的Role"""
        role.set_env(self)
        self.roles[role.profile] = role

    def add_roles(self, roles: Iterable[Role]):
        """增加一批在当前环境的Role"""
        for role in roles:
            self.add_role(role)

    def _parser_roles(self, text):
        """解析添加的Roles"""
        agents = re.findall('{[\s\S]*?}', text) # re.findall('{{.*}}', agents)
        agents_args = []
        for agent in agents:
            agent = json.loads(agent.strip())
            if len(agent.keys()) > 0:
                agents_args.append(agent)

        print('---------------Agents---------------')
        for i, agent in enumerate(agents_args):
            print('Role', i, agent)

        return agents_args

    def _parser_plan(self, context):
        """解析生成的计划Plan"""
        plan_context = re.findall('## Revised Execution Plan([\s\S]*?)##', str(context))[0]
        steps = [v.split("\n")[0] for v in re.split("\n\d+\. ", plan_context)[1:]]
        print('---------------Steps---------------')
        for i, step in enumerate(steps):
            print('Step', i, step)

        return steps

    def create_roles(self, plan: list, args: dict):
        """Create Role instances based on the provided plan and arguments."""
        init_actions, watch_actions = [], []
        for role in args:
            requirement_type = self.requirement_factory(role['name'])
            print('Add a new role:', role['name'])
            self.add_role(CustomRole(
                name=role['name'],
                profile=role['name'],
                goal=role['descriptions'],
                role_prompt=role['prompt'],
                steps=role['steps'],
                tool=role['tools'],
                watch_actions=[requirement_type],
                proxy=self.proxy,
                llm_api_key=self.llm_api_key,
                serpapi_key=self.serpapi_key,
            ))
            watch_actions.append(requirement_type)
            init_actions.append(self.get_role(role['name']).init_actions)

        init_actions.append(Requirement)
        self.add_role(ActionObserver(steps=plan, watch_actions=init_actions, init_actions=watch_actions, proxy=self.proxy, llm_api_key=self.llm_api_key))

    async def publish_message(self, message: Message):
        """向当前环境发布信息"""
        # self.message_queue.put(message)
        self.memory.add(message)
        self.history += f"\n{message}"

        if 'Plan Observer' in message.role:
            self.steps = self._parser_plan(message.content)
            self.new_roles = self.create_roles(self.steps, self.new_roles_args)

        parsed_content = self._parse_message_content(message)
        if parsed_content:
            filename, file_content = parsed_content

        if message.role and 'ActionObserver' != message.role:
            msg = self._format_message_for_queue(message, filename, file_content)
            if self.alg_msg_queue:
                self.alg_msg_queue.put_nowait(msg)

        if 'Agents Observer' in message.role:
            self.new_roles_args = self._parser_roles(message.content)
            msg = self._format_message_for_queue(message)
            if self.alg_msg_queue:
                self.alg_msg_queue.put_nowait(msg)

    def _parse_message_content(self, message: Message):
        """Parse the content of the message and return the filename and file content if present."""
        # Use a hash of the message content as the cache key
        cache_key = hash(message.content)
        # Check if we have already parsed this message content
        if cache_key in self._content_cache:
            return self._content_cache[cache_key]

        filename, file_content = None, None
        if hasattr(message.instruct_content, 'Type') and 'FILE' in message.instruct_content.Type:
            filename = message.instruct_content.Key
            file_type = re.findall('```(.*?)\n', str(message.content))[0]
            file_content = re.findall(f'```{file_type}([\s\S]*?)```', str(message.content))[0]
            # Store the parsed content in the cache
            self._content_cache[cache_key] = (filename, file_content)

        return filename, file_content

    def _format_message_for_queue(self, message: Message, filename=None, file_content=None):
        """Format the message for adding to the message queue."""
        msg = {
            'timestamp': timestamp(),
            'role': message.role,
            'content': message.content,
            'file': {
                'file_type': filename,
                'file_data': file_content,
            }
        }
        return format_message(action=MessageType.RunTask.value, data={'task_id': self.task_id, 'task_message': msg})

    async def run(self, k=1):
        """处理一次所有Role的运行"""
        old_roles = []
        for _ in range(k):
            futures = []
            for key in self.roles.keys():
                old_roles.append(key)
                role = self.roles[key]
                future = role.run()
                futures.append(future)

            await asyncio.gather(*futures)

        if len(old_roles) < len(self.roles):
            for _ in range(int(2*len(self.steps))):
                futures = []
                for key in self.roles.keys():
                    # if key not in old_roles:
                    #     old_roles.append(key)
                    role = self.roles[key]
                    future = role.run()
                    futures.append(future)

                await asyncio.gather(*futures)

    def get_roles(self) -> dict[str, Role]:
        """获得环境内的所有Role"""
        return self.roles

    def get_role(self, name: str) -> Role:
        """获得环境内的指定Role"""
        return self.roles.get(name, None)

    def requirement_factory(self, role_name: str):
        """Factory method to create Requirement instances based on role name."""
        # Mapping of role names to Requirement subclasses
        requirement_classes = {
            # 'Manager': ManagerRequirement,  # This line will be removed as ManagerRequirement is not defined
            'Observer': ObserverRequirement,
            # Add mappings for other roles as needed
        }
        # Get the Requirement subclass based on role name, default to generic Requirement if not found
        requirement_class = requirement_classes.get(role_name.replace(' ', '_'), Requirement)
        # Instantiate and return the Requirement subclass
        return requirement_class()
