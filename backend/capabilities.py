CAPABILITIES = {
    "terraform": {
        "description": "Terraform Cloud APIs",
        "version": "v2",
        "resources": {

            # =====================================================
            # ORGANIZATIONS
            # =====================================================
            "organization": {
                "description": "Terraform Cloud Organizations",
                "actions": {

                    "list": {
                        "description": "List all Terraform Cloud organizations accessible to the user.",
                        "http": {
                            "method": "GET",
                            "path": "/api/v2/organizations"
                        },
                        "input_schema": {
                            "type": "object",
                            "properties": {
                                "q": {
                                    "type": "string",
                                    "description": "Search by name or notification email."
                                },
                                "q[name]": {
                                    "type": "string",
                                    "description": "Search organizations by name."
                                },
                                "q[email]": {
                                    "type": "string",
                                    "description": "Search organizations by notification email."
                                },
                                "page[number]": {
                                    "type": "integer",
                                    "minimum": 1
                                },
                                "page[size]": {
                                    "type": "integer",
                                    "minimum": 1
                                }
                            },
                            "required": []
                        },
                        "output_schema": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "org_id": {
                                        "type": "string",
                                        "description": "Organization name (primary identifier)."
                                    },
                                    "org_name": {
                                        "type": "string",
                                        "description": "Organization display name."
                                    },
                                    "external_id": {
                                        "type": "string"
                                    },
                                    "email": {
                                        "type": "string"
                                    },
                                    "created_at": {
                                        "type": "string",
                                        "format": "date-time"
                                    }
                                },
                                "required": ["org_id", "org_name"]
                            }
                        },
                        "effects": "read"
                    },

                    "get": {
                        "description": "Get details of a specific Terraform Cloud organization.",
                        "http": {
                            "method": "GET",
                            "path": "/api/v2/organizations/{organization_name}"
                        },
                        "input_schema": {
                            "type": "object",
                            "properties": {
                                "organization_name": {
                                    "type": "string",
                                    "description": "Organization name."
                                }
                            },
                            "required": ["organization_name"]
                        },
                        "output_schema": {
                            "type": "object",
                            "properties": {
                                "org_id": { "type": "string" },
                                "org_name": { "type": "string" },
                                "external_id": { "type": "string" },
                                "email": { "type": "string" },
                                "created_at": {
                                    "type": "string",
                                    "format": "date-time"
                                }
                            },
                            "required": ["org_id", "org_name"]
                        },
                        "effects": "read"
                    },

                    "create": {
                        "description": "Create a new Terraform Cloud organization.",
                        "http": {
                            "method": "POST",
                            "path": "/api/v2/organizations"
                        },
                        "input_schema": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Organization name."
                                },
                                "email": {
                                    "type": "string",
                                    "description": "Admin email."
                                }
                            },
                            "required": ["name", "email"]
                        },
                        "output_schema": {
                            "type": "object",
                            "properties": {
                                "org_id": { "type": "string" },
                                "external_id": { "type": "string" },
                                "created_at": {
                                    "type": "string",
                                    "format": "date-time"
                                }
                            },
                            "required": ["org_id"]
                        },
                        "effects": "write"
                    },

                    "get_entitlement_set": {
                        "description": "Retrieve the entitlement set for an organization.",
                        "http": {
                            "method": "GET",
                            "path": "/api/v2/organizations/{organization_name}/entitlement-set"
                        },
                        "input_schema": {
                            "type": "object",
                            "properties": {
                                "organization_name": {
                                    "type": "string"
                                }
                            },
                            "required": ["organization_name"]
                        },
                        "output_schema": {
                            "type": "object",
                            "properties": {
                                "agents": { "type": "boolean" },
                                "audit_logging": { "type": "boolean" },
                                "cost_estimation": { "type": "boolean" },
                                "policy_enforcement": { "type": "boolean" },
                                "user_limit": { "type": "integer" }
                            },
                            "required": []
                        },
                        "effects": "read"
                    }
                }
            }

            # 👉 later: workspace, runs, variables, etc.
        }
    },
    # =====================================================
    # LLM (GENERAL PURPOSE REASONING ENGINE)
    # =====================================================
    "llm": {
        "description": (
            "General-purpose Large Language Model capable of reasoning, "
            "filtering, transforming, generating, and analyzing data "
            "based on natural language instructions."
        ),
        "version": "v1",
        "resources": {
            "generic": {
                "description": "Unstructured semantic reasoning over workflow context",
                "actions": {
                    "run": {
                        "description": (
                            "Execute an arbitrary reasoning task defined entirely "
                            "by the prompt. The LLM may filter, transform, generate, "
                            "summarize, classify, or analyze data."
                        ),
                        "input_schema": {
                            "type": "object",
                            "additionalProperties": True,
                            "description": "Full workflow context (unrestricted)"
                        },
                        "output_schema": {
                            "type": "object",
                            "additionalProperties": True,
                            "description": "Any JSON output produced by the LLM"
                        },
                        "effects": "semantic"
                    }
                }
            }
        }
    },
    # =====================================================
    # CONFLUENCE (EXAMPLE STUB)
    # =====================================================
    "confluence": {
        "description": "Atlassian Confluence APIs",
        "version": "v1",
        "resources": {
            "page": {
                "description": "Confluence Pages",
                "actions": {
                    "create": {
                        "description": "Create a Confluence page.",
                        "http": {
                            "method": "POST",
                            "path": "/wiki/rest/api/content"
                        },
                        "input_schema": {
                            "type": "object",
                            "properties": {
                                "title": { "type": "string" },
                                "content": { "type": "string" }
                            },
                            "required": ["title", "content"]
                        },
                        "output_schema": {
                            "type": "object",
                            "properties": {
                                "page_url": { "type": "string" }
                            },
                            "required": ["page_url"]
                        },
                        "effects": "write"
                    }
                }
            }
        }
    },

    # =====================================================
    # INTERNAL FILTER (NOT API-BACKED)
    # =====================================================
    "filter": {
        "description": "Internal data filtering",
        "version": "v1",
        "resources": {
            "generic": {
                "actions": {
                    "apply": {
                        "description": "Filter data based on conditions.",
                        "input_schema": {
                            "type": "object",
                            "additionalProperties": True
                        },
                        "output_schema": {
                            "type": "object",
                            "additionalProperties": True
                        },
                        "effects": "transform"
                    }
                }
            }
        }
    }
}
