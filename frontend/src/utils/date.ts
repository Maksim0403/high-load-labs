export const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('uk-UA', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

export const formatTime = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleTimeString('uk-UA', { hour: '2-digit', minute: '2-digit' })
}

export const formatAlertDate = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return (
    date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) +
    ', ' +
    date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false })
  )
}
