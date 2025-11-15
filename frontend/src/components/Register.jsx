import React, { useState } from 'react';
import axios from 'axios';

function Register() {

    const [name, setName] = useState("")
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const data={name,email,password}

    const  handleRegister = async () => {
        try {
            const response = await axios.post('http://127.0.0.1:8000/api/v1/general/register', data);

            console.log('Success:', response.data);
        } catch (error) {
            console.error('Error:', error.message);
        }
    }

    return (
        <>
            <div><h1>Regiter</h1></div>
            <div>
                <input type="text" value={name} onChange={(e) => { setName(e.target.value) }} placeholder='Name' />
                <input type="text" value={email} onChange={(e) => { setEmail(e.target.value) }} placeholder='Email/Username' />
                <input type="text" value={password} onChange={(e) => { setPassword(e.target.value) }} placeholder='Password' />
                <button onClick={handleRegister}>Register</button>
            </div>
        </>
    )
}

export default Register