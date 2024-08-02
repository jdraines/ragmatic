1. Find all modules with a specific import:

```python
query = {
    "query": {
        "match": {
            "imports": "pandas"
        }
    }
}
```

2. Search for modules containing a specific term in their summary:

```python
query = {
    "query": {
        "match": {
            "summary": "data processing"
        }
    }
}
```

3. Find classes that are abstract:

```python
query = {
    "query": {
        "nested": {
            "path": "classes",
            "query": {
                "term": {
                    "classes.is_abstract": True
                }
            }
        }
    }
}
```

4. Search for functions with a specific return type:

```python
query = {
    "query": {
        "nested": {
            "path": "functions",
            "query": {
                "term": {
                    "functions.return_type": "List[str]"
                }
            }
        }
    }
}
```

5. Find methods with high cyclomatic complexity:

```python
query = {
    "query": {
        "nested": {
            "path": "classes.methods",
            "query": {
                "range": {
                    "classes.methods.metrics.cyclomatic_complexity": {
                        "gte": 10
                    }
                }
            }
        }
    }
}
```

6. Search for classes with specific base classes:

```python
query = {
    "query": {
        "nested": {
            "path": "classes",
            "query": {
                "terms": {
                    "classes.bases": ["AbstractBaseClass", "Interface"]
                }
            }
        }
    }
}
```

7. Find modules with high instability:

```python
query = {
    "query": {
        "range": {
            "metrics.instability": {
                "gte": 0.7
            }
        }
    }
}
```

8. Search for functions or methods that use a specific parameter type:

```python
query = {
    "query": {
        "bool": {
            "should": [
                {
                    "nested": {
                        "path": "functions",
                        "query": {
                            "match": {
                                "functions.params": "DataFrame"
                            }
                        }
                    }
                },
                {
                    "nested": {
                        "path": "classes.methods",
                        "query": {
                            "match": {
                                "classes.methods.params": "DataFrame"
                            }
                        }
                    }
                }
            ]
        }
    }
}
```

9. Aggregate to find the average number of methods per class:

```python
query = {
    "size": 0,
    "aggs": {
        "classes": {
            "nested": {
                "path": "classes"
            },
            "aggs": {
                "method_count": {
                    "nested": {
                        "path": "classes.methods"
                    }
                },
                "avg_methods": {
                    "avg_bucket": {
                        "buckets_path": "method_count>_count"
                    }
                }
            }
        }
    }
}
```

10. Find modules with functions that have multiple return types:

```python
query = {
    "query": {
        "nested": {
            "path": "functions",
            "query": {
                "script": {
                    "script": {
                        "source": "doc['functions.return_type'].value.contains(' | ')"
                    }
                }
            }
        }
    }
}
```
