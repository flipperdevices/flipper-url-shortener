import { Notify } from 'quasar'

const showNotif = ({ message, color, reloadBtn, timeout = 0 }) => {
  const actions = []

  if (reloadBtn) {
    actions.push({ label: 'Reload', color: 'white', handler: () => { location.reload() } })
  }
  if (actions.length === 0) {
    actions.push({ icon: 'close', color: 'white', class: 'q-px-sm' })
  } else {
    actions.push({ label: 'Dismiss', color: 'white' })
  }

  Notify.create({
    message,
    color,
    textColor: 'white',
    position: 'bottom-right',
    timeout,
    group: true,
    actions
  })
}

export default showNotif
