# Release Notes Generator

---

## Tollgate Key

Enter the tollgate key to generate release notes.

[Tollgate Key Input Field]   [Generate Button]

Example:
TG-12345

---

## Status

Current Status: **Draft** / **Published**

---

## Generated Release Notes

Editable content area where generated release notes will appear.
Users can modify the content before saving or publishing.
+----------------------------------------------------+
|              Release Notes Generator               |
+----------------------------------------------------+

+----------------------------------------------------+
|              Release Notes Generator               |
+----------------------------------------------------+

Tollgate Key

[ Enter Tollgate Key ]     [ Generate ]


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

[ Save Draft ]            [ Publish to Confluence ]

---

## Actions

[ Save Draft ]    [ Publish to Confluence ]

---

## Workflow

1. User enters **Tollgate Key**
2. Click **Generate**
3. Backend generates release notes
4. Notes appear in editor
5. User edits if needed
6. Click **Save Draft** → stored in database
7. Click **Publish to Confluence** → publishes the saved notes

Project Folder Structure 
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
└── App.jsx

