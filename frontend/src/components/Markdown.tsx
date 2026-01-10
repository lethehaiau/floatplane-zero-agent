import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism'

interface MarkdownProps {
  content: string
}

export function Markdown({ content }: MarkdownProps) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        code({ className, children, ...props }) {
          const match = /language-(\w+)/.exec(className || '')
          const isInline = !match && !String(children).includes('\n')

          if (isInline) {
            return (
              <code className="bg-gray-100 px-1.5 py-0.5 rounded text-sm font-mono" {...props}>
                {children}
              </code>
            )
          }

          return (
            <div className="my-4 rounded-lg overflow-hidden border border-gray-200">
              {match && (
                <div className="bg-gray-100 px-4 py-2 text-xs text-gray-600 border-b border-gray-200">
                  {match[1]}
                </div>
              )}
              <SyntaxHighlighter
                style={oneLight}
                language={match ? match[1] : 'text'}
                PreTag="div"
                customStyle={{
                  margin: 0,
                  padding: '1rem',
                  fontSize: '0.875rem',
                  background: '#fafafa',
                }}
              >
                {String(children).replace(/\n$/, '')}
              </SyntaxHighlighter>
            </div>
          )
        },
        p({ children }) {
          return <p className="mb-4 last:mb-0">{children}</p>
        },
        ul({ children }) {
          return <ul className="list-disc list-inside mb-4 space-y-1">{children}</ul>
        },
        ol({ children }) {
          return <ol className="list-decimal list-inside mb-4 space-y-1">{children}</ol>
        },
        li({ children }) {
          return <li className="ml-2">{children}</li>
        },
        h1({ children }) {
          return <h1 className="text-2xl font-bold mb-4 mt-6 first:mt-0">{children}</h1>
        },
        h2({ children }) {
          return <h2 className="text-xl font-bold mb-3 mt-5 first:mt-0">{children}</h2>
        },
        h3({ children }) {
          return <h3 className="text-lg font-bold mb-2 mt-4 first:mt-0">{children}</h3>
        },
        blockquote({ children }) {
          return (
            <blockquote className="border-l-4 border-gray-300 pl-4 my-4 text-gray-600 italic">
              {children}
            </blockquote>
          )
        },
        a({ href, children }) {
          return (
            <a href={href} className="text-blue-600 hover:underline" target="_blank" rel="noopener noreferrer">
              {children}
            </a>
          )
        },
        table({ children }) {
          return (
            <div className="overflow-x-auto my-4">
              <table className="min-w-full border border-gray-200">{children}</table>
            </div>
          )
        },
        thead({ children }) {
          return <thead className="bg-gray-50">{children}</thead>
        },
        th({ children }) {
          return <th className="border border-gray-200 px-4 py-2 text-left font-medium">{children}</th>
        },
        td({ children }) {
          return <td className="border border-gray-200 px-4 py-2">{children}</td>
        },
        hr() {
          return <hr className="my-6 border-gray-200" />
        },
        strong({ children }) {
          return <strong className="font-semibold">{children}</strong>
        },
      }}
    >
      {content}
    </ReactMarkdown>
  )
}
