'use client'

import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Placeholder from '@tiptap/extension-placeholder'
import { Bold, Italic, List, ListOrdered, Heading1, Heading2 } from 'lucide-react'

interface RichTextEditorProps {
    content: string
    onChange: (content: string) => void
    placeholder?: string
}

export function RichTextEditor({ content, onChange, placeholder }: RichTextEditorProps) {
    const editor = useEditor({
        extensions: [
            StarterKit,
            Placeholder.configure({
                placeholder: placeholder || 'Start writing...',
            }),
        ],
        content,
        onUpdate: ({ editor }) => {
            onChange(editor.getHTML())
        },
        editorProps: {
            attributes: {
                class: 'prose prose-sm max-w-none focus:outline-none min-h-[200px] px-4 py-3',
            },
        },
    })

    if (!editor) {
        return null
    }

    return (
        <div className="border border-gray-300 rounded-lg overflow-hidden">
            {/* Toolbar */}
            <div className="bg-gray-50 border-b border-gray-300 p-2 flex gap-1">
                <button
                    onClick={() => editor.chain().focus().toggleBold().run()}
                    className={`p-2 rounded hover:bg-gray-200 transition ${editor.isActive('bold') ? 'bg-gray-200' : ''
                        }`}
                    type="button"
                >
                    <Bold className="w-4 h-4" />
                </button>
                <button
                    onClick={() => editor.chain().focus().toggleItalic().run()}
                    className={`p-2 rounded hover:bg-gray-200 transition ${editor.isActive('italic') ? 'bg-gray-200' : ''
                        }`}
                    type="button"
                >
                    <Italic className="w-4 h-4" />
                </button>
                <div className="w-px bg-gray-300 mx-1"></div>
                <button
                    onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
                    className={`p-2 rounded hover:bg-gray-200 transition ${editor.isActive('heading', { level: 1 }) ? 'bg-gray-200' : ''
                        }`}
                    type="button"
                >
                    <Heading1 className="w-4 h-4" />
                </button>
                <button
                    onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
                    className={`p-2 rounded hover:bg-gray-200 transition ${editor.isActive('heading', { level: 2 }) ? 'bg-gray-200' : ''
                        }`}
                    type="button"
                >
                    <Heading2 className="w-4 h-4" />
                </button>
                <div className="w-px bg-gray-300 mx-1"></div>
                <button
                    onClick={() => editor.chain().focus().toggleBulletList().run()}
                    className={`p-2 rounded hover:bg-gray-200 transition ${editor.isActive('bulletList') ? 'bg-gray-200' : ''
                        }`}
                    type="button"
                >
                    <List className="w-4 h-4" />
                </button>
                <button
                    onClick={() => editor.chain().focus().toggleOrderedList().run()}
                    className={`p-2 rounded hover:bg-gray-200 transition ${editor.isActive('orderedList') ? 'bg-gray-200' : ''
                        }`}
                    type="button"
                >
                    <ListOrdered className="w-4 h-4" />
                </button>
            </div>

            {/* Editor */}
            <EditorContent editor={editor} />
        </div>
    )
}
