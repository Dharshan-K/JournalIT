import {useEffect} from "react"

function Home(){

	useEffect(()=>{
		const query = new URLSearchParams(window.location.search);

		const githubCode = query.get('code');
		const state = query.get('state');
		const url = `https://github.com/login/oauth/access_token?`
		console.log("code, state", githubCode, state)
		async function fetchData(){
			await fetch(`http://34.203.40.83:8000/getUserAccessToken?code=${githubCode}&state=${state}&scope=repo`, {
				method: "GET"
			}).then(async (response)=>{
				const data = await response.json()
				console.log(data)
				await fetch(`http://34.203.40.83:8000/events?code=${data.access_token}`, {
					method: "GET",
				}).then(async(response)=>{
					const data = await response.json();
					console.log("events", data)
				})
				// await fetch("https://api.github.com/user/repos", {
				// 	method: "POST",
				// 	headers : {
				// 		"Authorization" : `Bearer ${data.access_token}`,
				// 		"Accept" : "application/vnd.github+json",
				// 		"X-GitHub-Api-Version": "2022-11-28",
				// 		"Content-Type": "application/json"
				// 	},
				// 	body : JSON.stringify({
				// 		"name" : "first API",
				// 		"description" : "Created from github API",
				// 		"private" : false
				// 	})
				// }).then(async(response)=>{
				// 	const data = await response.json();
				// 	console.log("response", data)
				// })
			})
		}

		fetchData()
	},[])
	return(
		<div><h1>Home</h1></div>
		)
}

export default Home