import { useState, useEffect, useRef } from 'react'
import Editor from '@monaco-editor/react'
import mermaid from 'mermaid'
import SplitPane from 'react-split-pane'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { 
  Save, 
  Download, 
  Share, 
  Eye, 
  Code, 
  FileText, 
  Sparkles,
  MessageSquare,
  History,
  GitBranch
} from 'lucide-react'

const Workbench = () => {
  const [content, setContent] = useState(`# Solution Architecture Document

## Context
We need to design a scalable e-commerce platform that can handle high traffic during peak shopping seasons.

## Requirements
- Handle 10,000+ concurrent users
- 99.9% uptime
- Sub-second response times
- PCI DSS compliance

## Architecture Decision Record

### Status
Proposed

### Context
The current monolithic architecture cannot scale to meet our growing user base and performance requirements.

### Decision
We will adopt a microservices architecture using containerized services on Kubernetes.

### Consequences
**Positive:**
- Better scalability and fault isolation
- Independent deployment of services
- Technology diversity for different services

**Negative:**
- Increased operational complexity
- Network latency between services
- Distributed system challenges

## System Architecture

\`\`\`mermaid
graph TB
    A[Load Balancer] --> B[API Gateway]
    B --> C[User Service]
    B --> D[Product Service]
    B --> E[Order Service]
    B --> F[Payment Service]
    
    C --> G[(User DB)]
    D --> H[(Product DB)]
    E --> I[(Order DB)]
    F --> J[(Payment DB)]
    
    K[Redis Cache] --> B
    L[Message Queue] --> E
    L --> F
\`\`\`

## Implementation Plan
1. Set up Kubernetes cluster
2. Containerize existing services
3. Implement API Gateway
4. Migrate data to microservices
5. Set up monitoring and logging`)

  const [activeTab, setActiveTab] = useState('editor')
  const [diagramHtml, setDiagramHtml] = useState('')
  const diagramRef = useRef(null)

  // Initialize Mermaid
  useEffect(() => {
    mermaid.initialize({
      startOnLoad: true,
      theme: 'default',
      securityLevel: 'loose',
    })
  }, [])

  // Extract and render Mermaid diagrams
  useEffect(() => {
    const extractMermaidDiagrams = async () => {
      const mermaidRegex = /```mermaid\n([\s\S]*?)\n```/g
      const matches = [...content.matchAll(mermaidRegex)]
      
      if (matches.length > 0) {
        try {
          const diagramCode = matches[0][1]
          const { svg } = await mermaid.render('diagram', diagramCode)
          setDiagramHtml(svg)
        } catch (error) {
          console.error('Mermaid rendering error:', error)
          setDiagramHtml('<p class="text-red-500">Error rendering diagram</p>')
        }
      } else {
        setDiagramHtml('')
      }
    }

    extractMermaidDiagrams()
  }, [content])

  const handleEditorChange = (value) => {
    setContent(value || '')
  }

  const renderMarkdown = (text) => {
    // Simple markdown rendering for demo
    return text
      .replace(/^# (.*$)/gim, '<h1 class="text-3xl font-bold mb-4">$1</h1>')
      .replace(/^## (.*$)/gim, '<h2 class="text-2xl font-semibold mb-3">$1</h2>')
      .replace(/^### (.*$)/gim, '<h3 class="text-xl font-medium mb-2">$1</h3>')
      .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
      .replace(/\*(.*)\*/gim, '<em>$1</em>')
      .replace(/```mermaid\n([\s\S]*?)\n```/g, '<div class="diagram-placeholder">Diagram rendered above</div>')
      .replace(/```(.*?)\n([\s\S]*?)\n```/g, '<pre class="bg-muted p-4 rounded-lg overflow-x-auto"><code>$2</code></pre>')
      .replace(/\n/g, '<br>')
  }

  return (
    <div className="h-full flex flex-col">
      {/* Toolbar */}
      <div className="h-12 border-b border-border bg-background px-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Badge variant="outline">E-commerce Platform</Badge>
          <span className="text-sm text-muted-foreground">•</span>
          <span className="text-sm text-muted-foreground">Last saved 2 minutes ago</span>
        </div>
        
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm">
            <History className="w-4 h-4 mr-2" />
            Version History
          </Button>
          <Button variant="ghost" size="sm">
            <MessageSquare className="w-4 h-4 mr-2" />
            Comments
          </Button>
          <Button variant="ghost" size="sm">
            <Sparkles className="w-4 h-4 mr-2" />
            AI Assist
          </Button>
          <Button variant="outline" size="sm">
            <Share className="w-4 h-4 mr-2" />
            Share
          </Button>
          <Button size="sm">
            <Save className="w-4 h-4 mr-2" />
            Save
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1">
        <SplitPane split="vertical" defaultSize="50%" minSize={300}>
          {/* Left Pane - Editor */}
          <div className="h-full flex flex-col">
            <div className="h-10 border-b border-border bg-muted/30 px-4 flex items-center">
              <Code className="w-4 h-4 mr-2" />
              <span className="text-sm font-medium">Editor</span>
            </div>
            <div className="flex-1">
              <Editor
                height="100%"
                defaultLanguage="markdown"
                value={content}
                onChange={handleEditorChange}
                theme="vs-light"
                options={{
                  minimap: { enabled: false },
                  fontSize: 14,
                  lineNumbers: 'on',
                  wordWrap: 'on',
                  automaticLayout: true,
                }}
              />
            </div>
          </div>

          {/* Right Pane - Preview */}
          <div className="h-full flex flex-col">
            <Tabs value={activeTab} onValueChange={setActiveTab} className="h-full flex flex-col">
              <div className="h-10 border-b border-border bg-muted/30 px-4 flex items-center">
                <TabsList className="h-8">
                  <TabsTrigger value="preview" className="text-xs">
                    <Eye className="w-3 h-3 mr-1" />
                    Preview
                  </TabsTrigger>
                  <TabsTrigger value="diagram" className="text-xs">
                    <GitBranch className="w-3 h-3 mr-1" />
                    Diagram
                  </TabsTrigger>
                  <TabsTrigger value="outline" className="text-xs">
                    <FileText className="w-3 h-3 mr-1" />
                    Outline
                  </TabsTrigger>
                </TabsList>
              </div>

              <div className="flex-1 overflow-auto">
                <TabsContent value="preview" className="h-full m-0">
                  <div className="p-6 prose prose-sm max-w-none">
                    <div 
                      dangerouslySetInnerHTML={{ 
                        __html: renderMarkdown(content) 
                      }} 
                    />
                  </div>
                </TabsContent>

                <TabsContent value="diagram" className="h-full m-0">
                  <div className="p-6">
                    {diagramHtml ? (
                      <div className="flex justify-center">
                        <div 
                          ref={diagramRef}
                          dangerouslySetInnerHTML={{ __html: diagramHtml }}
                          className="max-w-full overflow-auto"
                        />
                      </div>
                    ) : (
                      <div className="text-center text-muted-foreground py-12">
                        <GitBranch className="w-12 h-12 mx-auto mb-4 opacity-50" />
                        <p>No diagrams found in the document</p>
                        <p className="text-sm">Add a Mermaid diagram using ```mermaid code blocks</p>
                      </div>
                    )}
                  </div>
                </TabsContent>

                <TabsContent value="outline" className="h-full m-0">
                  <div className="p-6">
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg">Document Outline</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2">
                          <div className="pl-0">
                            <a href="#" className="text-sm font-medium hover:text-primary">
                              Solution Architecture Document
                            </a>
                          </div>
                          <div className="pl-4">
                            <a href="#" className="text-sm text-muted-foreground hover:text-primary">
                              Context
                            </a>
                          </div>
                          <div className="pl-4">
                            <a href="#" className="text-sm text-muted-foreground hover:text-primary">
                              Requirements
                            </a>
                          </div>
                          <div className="pl-4">
                            <a href="#" className="text-sm text-muted-foreground hover:text-primary">
                              Architecture Decision Record
                            </a>
                          </div>
                          <div className="pl-8">
                            <a href="#" className="text-sm text-muted-foreground hover:text-primary">
                              Status
                            </a>
                          </div>
                          <div className="pl-8">
                            <a href="#" className="text-sm text-muted-foreground hover:text-primary">
                              Context
                            </a>
                          </div>
                          <div className="pl-8">
                            <a href="#" className="text-sm text-muted-foreground hover:text-primary">
                              Decision
                            </a>
                          </div>
                          <div className="pl-8">
                            <a href="#" className="text-sm text-muted-foreground hover:text-primary">
                              Consequences
                            </a>
                          </div>
                          <div className="pl-4">
                            <a href="#" className="text-sm text-muted-foreground hover:text-primary">
                              System Architecture
                            </a>
                          </div>
                          <div className="pl-4">
                            <a href="#" className="text-sm text-muted-foreground hover:text-primary">
                              Implementation Plan
                            </a>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                </TabsContent>
              </div>
            </Tabs>
          </div>
        </SplitPane>
      </div>
    </div>
  )
}

export default Workbench
