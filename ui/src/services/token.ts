export function getTokenFromCookie(name: 'access' | 'refresh') {
  return localStorage.getItem(`${name}_token`);
}


export function setTokensToCookies(token: string, tokenType: 'access' | 'refresh', maxAge?:number) {
  console.log(maxAge)
  localStorage.setItem(`${tokenType}_token`, token);
}

export function removeTokensFromCookies(tokenType: 'access' | 'refresh') {
  localStorage.removeItem(`${tokenType}_token`);
}