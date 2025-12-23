#!/bin/bash

# Output the development principles reminder as structured hook output
cat <<'EOF'
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "🎯 DEVELOPMENT PRINCIPLES - MANDATORY REMINDER\n\nYou MUST query the Memory Bank for our development principles BEFORE starting any work:\n\n*Action Required:\nUse mcp__allpepper-memory-bank__memory_bank_read with:\n- projectName: 'main'\n- fileName: 'startup-idioms-and-principles.md'\n\nOur 7 Core Principles:*\n1. Ship is Better Than Done - Ship often, iterate\n2. Test, Test, and Test, Baby! - Don't break existing features\n3. Fast is Fine, Accuracy is Final - Build RIGHT thing first time\n4. In Doubt, Ask - No ego in uncertainty\n5. Ego Has Killed More Startups - Accept blind spots\n6. Be the Kepler - Prefer hard truth to dear delusions\n7. Occam's Razor - Choose simplicity, count assumptions\n\n⚠️ Load the full document now before proceeding with any tasks.\n\nAlso, Use Sequential Thinking MCP Server where ever applicable.\n\n Use Context7 MCP server to get the documentation for the libaries you are using/\n\n Use, LSP servers where ever applicable."
  }
}
EOF
