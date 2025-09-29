import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { 
  Menu, 
  Search, 
  Settings, 
  User, 
  FileText, 
  GitBranch, 
  Lightbulb,
  Users,
  Database,
  Zap,
  Plus,
  Bell
} from 'lucide-react'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Badge } from '@/components/ui/badge'

const Layout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(true)

  const sidebarItems = [
    { icon: FileText, label: 'Projects', count: 3, active: true },
    { icon: GitBranch, label: 'ADRs', count: 12 },
    { icon: Lightbulb, label: 'Knowledge Hub', count: 45 },
    { icon: Users, label: 'Collaboration' },
    { icon: Database, label: 'Integrations' },
    { icon: Zap, label: 'AI Oracle' },
  ]

  return (
    <div className="h-screen flex bg-background">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-64' : 'w-16'} transition-all duration-300 bg-sidebar border-r border-sidebar-border flex flex-col`}>
        {/* Sidebar Header */}
        <div className="p-4 border-b border-sidebar-border">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <Zap className="w-5 h-5 text-primary-foreground" />
            </div>
            {sidebarOpen && (
              <div>
                <h1 className="font-semibold text-sidebar-foreground">SA Platform</h1>
                <p className="text-xs text-sidebar-foreground/60">Solution Architect</p>
              </div>
            )}
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4">
          <div className="space-y-2">
            {sidebarItems.map((item, index) => (
              <button
                key={index}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition-colors ${
                  item.active 
                    ? 'bg-sidebar-accent text-sidebar-accent-foreground' 
                    : 'text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground'
                }`}
              >
                <item.icon className="w-5 h-5 flex-shrink-0" />
                {sidebarOpen && (
                  <>
                    <span className="flex-1">{item.label}</span>
                    {item.count && (
                      <Badge variant="secondary" className="text-xs">
                        {item.count}
                      </Badge>
                    )}
                  </>
                )}
              </button>
            ))}
          </div>
        </nav>

        {/* Sidebar Footer */}
        <div className="p-4 border-t border-sidebar-border">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="w-full justify-start"
          >
            <Menu className="w-4 h-4" />
            {sidebarOpen && <span className="ml-2">Collapse</span>}
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="h-16 border-b border-border bg-background px-6 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
              <Input
                placeholder="Search projects, ADRs, knowledge..."
                className="pl-10 w-96"
              />
            </div>
          </div>

          <div className="flex items-center gap-4">
            <Button variant="outline" size="sm">
              <Plus className="w-4 h-4 mr-2" />
              New Project
            </Button>
            
            <Button variant="ghost" size="sm" className="relative">
              <Bell className="w-4 h-4" />
              <Badge className="absolute -top-1 -right-1 w-2 h-2 p-0 bg-destructive" />
            </Button>

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="sm">
                  <User className="w-4 h-4 mr-2" />
                  John Doe
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuLabel>My Account</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem>
                  <User className="w-4 h-4 mr-2" />
                  Profile
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <Settings className="w-4 h-4 mr-2" />
                  Settings
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem>
                  Log out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </header>

        {/* Content Area */}
        <main className="flex-1 overflow-hidden">
          {children}
        </main>
      </div>
    </div>
  )
}

export default Layout
