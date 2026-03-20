/**
 * NCCN Monitor — OpenClaw Plugin
 *
 * Wraps the Python MCP server as a native OpenClaw plugin.
 * Tools appear directly in OpenClaw's tool list (like feishu_chat, etc.)
 * without needing mcporter as middleware.
 */
import { join } from "node:path";
import { existsSync } from "node:fs";
import type { OpenClawPluginApi } from "openclaw/plugin-sdk";
import { McpBridge } from "./src/mcp-bridge.js";
import {
  createCheckUpdatesTool,
  createGetStatusTool,
  createListGuidelinesTool,
  createFindGuidelineTool,
  createUpdateWatchListTool,
  createBrowseGuidelinesTool,
} from "./src/tools.js";

// Default paths — can be overridden via plugin config in openclaw.json
const DEFAULT_PROJECT_DIR = join(process.env.HOME ?? "", "Workspace/Claude/nccn_watcher");
const DEFAULT_PYTHON_PATH = join(DEFAULT_PROJECT_DIR, ".venv/bin/python");

const nccnMonitorPlugin = {
  id: "nccn-monitor",
  name: "NCCN Monitor",
  description: "Monitor NCCN clinical guideline updates",

  register(api: OpenClawPluginApi) {
    // Read config from api.pluginConfig (set in openclaw.json plugins.entries)
    const pluginCfg = api.pluginConfig ?? {};
    const enabled = pluginCfg.enabled !== false;
    const pythonPath = (pluginCfg.pythonPath as string) || DEFAULT_PYTHON_PATH;
    const projectDir = (pluginCfg.projectDir as string) || DEFAULT_PROJECT_DIR;

    if (!enabled) {
      api.logger.info("[nccn-monitor] Plugin disabled");
      return;
    }

    // Validate paths
    if (!existsSync(pythonPath)) {
      api.logger.warn(
        `[nccn-monitor] Python not found at ${pythonPath}. ` +
          `Run: cd ${projectDir} && uv venv .venv && uv pip install -e .`,
      );
      return;
    }

    const bridge = new McpBridge(pythonPath, projectDir);

    // Register all 6 tools
    api.registerTool(() => createCheckUpdatesTool(bridge));
    api.registerTool(() => createGetStatusTool(bridge));
    api.registerTool(() => createListGuidelinesTool(bridge));
    api.registerTool(() => createFindGuidelineTool(bridge));
    api.registerTool(() => createUpdateWatchListTool(bridge));
    api.registerTool(() => createBrowseGuidelinesTool(bridge));

    api.logger.info(
      `[nccn-monitor] Registered 6 tools (python=${pythonPath}, project=${projectDir})`,
    );
  },
};

export default nccnMonitorPlugin;
