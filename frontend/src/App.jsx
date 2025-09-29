import Layout from './components/Layout'
import Workbench from './components/Workbench'
import AIOracle from './components/AIOracle'
import './App.css'

function App() {
  return (
    <Layout>
      <div className="flex h-full">
        <div className="flex-1">
          <Workbench />
        </div>
        <AIOracle />
      </div>
    </Layout>
  )
}

export default App
