import { Link } from "react-router-dom"

function Home() {
  return (
    <div>
        <h1>CRM</h1>
        <Link to="/Login">Login</Link>&nbsp;&nbsp;&nbsp;&nbsp;
        <Link to="/Register">Register</Link>
    </div>
  )
}

export default Home