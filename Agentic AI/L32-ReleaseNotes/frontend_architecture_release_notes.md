
# Release Notes Generator – Frontend Architecture

## Overview

The **Release Notes Generator** is a one‑page frontend application built using React.
It allows users to:

- Enter a **Tollgate Key**
- Generate **Release Notes** from the backend
- Edit the generated release notes
- Save them as a **draft in the database**
- Publish them to **Confluence**

The frontend communicates with a **FastAPI backend** through REST APIs.

---

# Technology Stack

## Core Framework
- React

## UI Component Library
- Material UI

Provides UI components such as:
- Container
- TextField
- Button
- Card
- Typography
- Stack

## HTTP Client
- Axios

Used for:
- Generating release notes
- Saving drafts
- Publishing to Confluence

## Markdown Rendering
- React Markdown

Used to render markdown content for preview.

## Rich Text Editor (Optional)
- Tiptap

Provides editing capabilities for release notes.

## Icons (Optional)
- Lucide Icons

---

# Project Structure

```
src
│
├── pages
│   └── ReleaseNotesPage.jsx
│
├── components
│   ├── TollgateInput.jsx
│   ├── ReleaseNotesEditor.jsx
│   └── ActionButtons.jsx
│
├── services
│   └── releaseNotesAPI.js
│
├── App.jsx
│
└── main.jsx
```

---

# Component Architecture

```
ReleaseNotesPage
 ├── TollgateInput
 ├── StatusIndicator
 ├── ReleaseNotesEditor
 └── ActionButtons
```

| Component | Responsibility |
|-----------|---------------|
| ReleaseNotesPage | Main layout and state management |
| TollgateInput | Tollgate key input and generate button |
| ReleaseNotesEditor | Editable release notes editor |
| ActionButtons | Save draft and publish buttons |

---

# UI Layout Specification

## Page Header

```
+----------------------------------------------------+
|              Release Notes Generator               |
+----------------------------------------------------+
```

---

## Tollgate Key Input

```
+----------------------------------------------------+
| Tollgate Key                                       |
|                                                    |
| [ Enter Tollgate Key ]      [ Generate ]           |
+----------------------------------------------------+
```

Example input:

```
TG-12345
```

---

## Status Indicator

```
Status: Draft
```

Possible states:

- Draft
- Published

---

## Release Notes Editor

```
+----------------------------------------------------+
|                Generated Release Notes             |
+----------------------------------------------------+
|                                                    |
|  ## Release Summary                                |
|  - Feature A added                                 |
|  - Performance improvements                        |
|                                                    |
|  ## Bug Fixes                                      |
|  - Fixed authentication issue                      |
|                                                    |
|  ## Improvements                                   |
|  - Updated UI components                           |
|                                                    |
|  (User can edit this content)                      |
|                                                    |
+----------------------------------------------------+
```

This section is implemented using a **Markdown editor or Rich Text editor**.

---

## Action Buttons

```
+----------------------------------------------------+
|                                                    |
|   [ Save Draft ]      [ Publish to Confluence ]    |
|                                                    |
+----------------------------------------------------+
```

### Save Draft
Stores the release notes in the database.

### Publish to Confluence
Publishes the saved release notes to Confluence.

---

# Complete Page Layout

```
+----------------------------------------------------+
|              Release Notes Generator               |
+----------------------------------------------------+

Tollgate Key

[ Enter Tollgate Key ]      [ Generate ]


Status: Draft


+----------------------------------------------------+
|                Generated Release Notes             |
+----------------------------------------------------+
|                                                    |
|  Editable Markdown / Rich Text Editor              |
|                                                    |
|  - Backend generated content appears here          |
|  - User can edit the content                       |
|                                                    |
+----------------------------------------------------+

[ Save Draft ]              [ Publish to Confluence ]
```

---

# Application Workflow

```
User enters Tollgate Key
        ↓
Click Generate
        ↓
Backend generates release notes
        ↓
Release notes appear in editor
        ↓
User edits notes if necessary
        ↓
Save Draft → Stored in database
        ↓
Publish → Sent to Confluence
```

---

# Backend API Integration

## Generate Release Notes

POST /generate-release-notes

Request Example:

```
{
  "tollgate_key": "TG-12345"
}
```

---

## Save Draft

POST /release-notes

Request Example:

```
{
  "tollgate_key": "TG-12345",
  "content": "release notes content",
  "status": "draft"
}
```

---

## Publish Release Notes

POST /publish-release-notes

This API publishes the release notes to Confluence.

---

# Example React Imports

```javascript
import React, { useState } from "react";
import axios from "axios";

import {
  Container,
  Typography,
  TextField,
  Button,
  Card,
  CardContent,
  Stack,
  Chip
} from "@mui/material";

import ReactMarkdown from "react-markdown";
```

---

# Final Frontend Stack

```
React
Material UI
Axios
React Markdown
Tiptap (optional)
Lucide Icons (optional)
```
