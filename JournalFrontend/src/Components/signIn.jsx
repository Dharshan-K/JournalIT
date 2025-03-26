function SignIn(){
	const url = "https://github.com/login/oauth/authorize?client_id=Iv23liiO4Kvnleoqb6nD&redirect_uri=http://localhost:5173/home&scope=user&state=random_string&scope=public_repo"

	const handleSignIn = () =>{
		window.location.href = url
	}
	return(
	<div>
      <button onClick={handleSignIn} id="SignIn">Sign in with Github.</button>
    </div>
)
}

export default SignIn