# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""Agentbox environment server components."""

try:
	from .AgentBox_environment import AgentboxEnvironment
except Exception:  # pragma: no cover
	# Keep package importable for tools that only need sibling modules
	# such as `server.graders` during validation.
	AgentboxEnvironment = None  # type: ignore[assignment]

__all__ = ["AgentboxEnvironment"]
