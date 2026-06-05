export const requiredRule = (message = '此项必填') => ({
  required: true,
  message,
  trigger: ['blur', 'change']
})

export function validatePhone(_rule, value, callback) {
  const text = String(value || '').trim()
  if (!text) {
    callback()
    return
  }
  const mobile = /^1[3-9]\d{9}$/
  const landline = /^0\d{2,3}-?\d{7,8}$/
  if (mobile.test(text) || landline.test(text)) callback()
  else callback(new Error('请输入正确的手机号或座机号'))
}

export function validatePositiveHours(_rule, value, callback) {
  const numberValue = Number(value)
  if (!Number.isFinite(numberValue) || numberValue <= 0) {
    callback(new Error('课时数必须大于 0'))
    return
  }
  callback()
}

export function validateNonNegativeNumber(_rule, value, callback) {
  const numberValue = Number(value)
  if (!Number.isFinite(numberValue) || numberValue < 0) {
    callback(new Error('数值不能小于 0'))
    return
  }
  callback()
}

export async function validateForm(formRef) {
  if (!formRef?.value) return true
  return formRef.value.validate().catch(() => false)
}
