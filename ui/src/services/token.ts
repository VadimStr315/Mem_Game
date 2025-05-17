export function getTokenFromCookie(name: 'access' | 'refresh') {
  const matches = document.cookie.match(new RegExp(
    "(?:^|; )" + `${name}_token`.replace(/([\\.$?*|{}\\(\\)\\[\]\\\\/\\+^])/g, '\\$1') + "=([^;]*)"));
  return matches ? decodeURIComponent(matches[1]) : undefined;
}


export function setTokensToCookies(token: string, tokenType: 'access' | 'refresh', maxAge?:number) {
  const maxAgeRefresh = import.meta.env.VITE_EXPIRE_REFRESH_TOKEN ? import.meta.env.VITE_EXPIRE_REFRESH_TOKEN : 172800
  const maxAgeAccess = import.meta.env.VITE_EXPIRE_ACCESS_TOKEN ? import.meta.env.VITE_EXPIRE_ACCESS_TOKEN : 7200
  const options:Record<string, string | number | boolean> = {
    path: '/',
    secure: import.meta.env.VITE_USE_SECURE === "1", 
    'max-age': maxAge ? maxAge : tokenType === 'access' ? maxAgeAccess : maxAgeRefresh
  };
  let updatedCookie = encodeURIComponent(`${tokenType}_token`) + "=" + encodeURIComponent(token);
  for (const optionKey in options) {
    updatedCookie += "; " + optionKey;
    const optionValue = options[optionKey];
    if (optionValue !== true) {
      updatedCookie += "=" + optionValue;
    }
  }

  document.cookie = updatedCookie;
}

export function removeTokensFromCookies(tokenType: 'access' | 'refresh') {
  setTokensToCookies("",`${tokenType}`, -1)
}