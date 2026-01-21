// 测试所有导入是否正常
import { Status, EmailType } from './src/types'
import { STATUS_MAP, EMAIL_TYPE_MAP } from './src/utils/constants'
import { formatDateTime, maskPassword } from './src/utils/format'

console.log('Status:', Status)
console.log('EmailType:', EmailType)
console.log('STATUS_MAP:', STATUS_MAP)
console.log('EMAIL_TYPE_MAP:', EMAIL_TYPE_MAP)
console.log('formatDateTime:', formatDateTime)
console.log('maskPassword:', maskPassword)

console.log('所有导入测试通过！')
