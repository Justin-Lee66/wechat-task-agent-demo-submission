# Production Extension

Recommended production path:

1. Use WeCom / Enterprise WeChat official APIs if the organization controls the group/workspace.
2. If only regular WeChat is available, use a semi-automated screenshot/OCR adapter on a controlled desktop.
3. Avoid unofficial hooks, reverse engineering, or reading private WeChat databases.
4. When OCR/vision bounding boxes are available, crop exact message regions for task evidence rather than showing full screenshot thumbnails.
5. Add a scheduler, queue, observability, audit logs, authentication, and human correction UI.
6. A Hermes-style scheduled agent workflow could orchestrate ingestion later, but it should remain outside this take-home runtime.
