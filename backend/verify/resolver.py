def resolve_inputs(steps: list):
    available_outputs = set()
    required_user_inputs = {}

    for step in steps:
        inputs = step.get("inputs", {})

        for name, source in inputs.items():
            if source == "FROM_CONTEXT":
                if name not in available_outputs:
                    raise ValueError(
                        f"Input '{name}' cannot be resolved from context"
                    )
            elif source == "USER_INPUT":
                required_user_inputs[name] = "string"

        outputs = step.get("outputs", [])

        # filter passthrough
        if step["kind"] == "filter" and not outputs:
            outputs = list(inputs.keys())

        for out in outputs:
            available_outputs.add(out)

    return required_user_inputs
