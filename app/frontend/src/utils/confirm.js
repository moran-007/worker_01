import { ElMessageBox } from 'element-plus'

export function confirmDanger(message, title = '请确认') {
  return ElMessageBox.confirm(message, title, {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    type: 'warning',
    autofocus: false
  })
}
