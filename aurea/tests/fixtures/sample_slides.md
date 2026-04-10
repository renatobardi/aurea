---
title: "Microservices for CTOs"
author: "Jane Dev"
theme: "default"
---

<!-- .slide: data-background="#0d0d0d" -->
# The Microservices Journey

From monolith to distributed systems

Note: Welcome everyone. This talk is about the architectural shift from monolithic
applications to microservices. We will cover trade-offs, patterns, and when to migrate.

---

## Why Microservices?

- Independent deployability
- Technology flexibility
- Team autonomy
- Scalability per service

Note: Each point corresponds to a real business driver. Independent deployability is
the most important — it enables teams to ship without coordinating releases.

---

## The Cost

Operational complexity increases **significantly**

Network calls replace function calls

Note: Don't skip this slide — set realistic expectations before committing to a
microservices architecture.

---

## When to Start

Deploy your monolith first.

Migrate when **team friction** exceeds **migration cost**

Note: Conway's Law applies here. Your architecture will mirror your organization.
A monolith is perfectly fine for teams smaller than 20 engineers.

---

## This Slide Has More Than Forty Words In The Body Text Which Should Trigger A Warning During Build Because The Limit Is Forty Words Per Slide Excluding Speaker Notes But Including All The Other Content

Warning trigger slide for testing purposes.

Note: This is the speaker note for the long slide. The word count above should
exceed 40 words and trigger a build warning.

```python
def example():
    """Code block for syntax highlighting test."""
    return "hello world"
```
