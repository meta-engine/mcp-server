"""Measurements supported by the recorded stream, without inferring token splits."""
import json


class StreamMetrics:
    def parse(self, lines):
        messages = set()
        tools = {}
        text_characters = 0
        seen_events = set()
        result = None
        for line_number, line in enumerate(lines, 1):
            if not line.strip():
                continue
            event = json.loads(line)
            event_id = event.get("uuid")
            if event_id is not None:
                if event_id in seen_events:
                    continue
                seen_events.add(event_id)
            if event.get("type") == "result":
                if result is not None:
                    raise ValueError("Multiple result events; aggregate sessions separately")
                result = event
            elif event.get("type") == "assistant":
                message = event["message"]
                message_id = message["id"]
                messages.add(message_id)
                for block in message["content"]:
                    if block["type"] == "text":
                        text_characters += len(block["text"])
                    elif block["type"] == "tool_use":
                        key = (message_id, block["id"])
                        serialized = json.dumps(block["input"], sort_keys=True)
                        if key in tools and tools[key] != serialized:
                            raise ValueError(f"Conflicting tool input at line {line_number}")
                        tools[key] = serialized
        if result is None or not result.get("usage") or not messages:
            raise ValueError("A complete session needs assistant messages and a result usage event")
        return {
            **result,
            "observations": {
                "version": 2,
                "assistant_messages": len(messages),
                "tool_calls": len(tools),
                "text_characters": text_characters,
                "tool_input_characters": sum(len(value) for value in tools.values()),
            },
        }
