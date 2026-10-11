# Interface Test Cases

## TC001 查询全部文章

### 请求信息

请求方式：

GET

URL:

https://jsonplaceholder.typicode.com/posts

### 测试目的

验证接口是否能够正常返回文章列表。

### 预期结果

1. 状态码200
2. 返回JSON数组
3. 包含文章数据

### 实际结果

1. 状态码200
2. 返回JSON数组
3. 包含多条文章记录

### 测试结果

Pass


## TC002 按用户ID查询文章

### 请求信息

请求方式：

GET

URL:

https://jsonplaceholder.typicode.com/posts?userId=1

### 测试目的

验证接口是否支持根据用户ID进行数据筛选。

### 测试方法

参数测试

### 测试数据

userId=1

### 预期结果

1. 状态码返回200
2. 返回数据格式为JSON数组
3. 所有返回数据的userId均为1

### 实际结果

1. 状态码200
2. 返回JSON数组
3. 所有文章记录userId均为1

### 测试结果

Pass


## TC003 查询无匹配数据

### 请求信息

请求方式：

GET

URL:

https://jsonplaceholder.typicode.com/posts?userId=999

### 测试目的

验证接口对于不存在查询条件的处理是否符合预期。

### 测试方法

异常场景测试

### 测试数据

userId=999

### 预期结果

1. 状态码返回200
2. 返回JSON数组
3. 数组为空

### 实际结果

1. 状态码200
2. 返回空数组[]
3. 没有文章记录

### 测试结果

Pass


## TC004 提交JSON数据

### 请求信息

请求方式：

POST

URL:

https://jsonplaceholder.typicode.com/posts

### 测试目的

验证接口是否能够正确接收JSON格式请求数据。

### 测试方法

接口数据校验测试

### 请求Body

```json
{
  "title": "Day6接口测试项目",
  "body": "TC004测试POST提交JSON数据",
  "userId": 1
}



---

# TC005 携带Token查询用户信息

```markdown
## TC005 Token认证访问用户信息


### 请求信息

请求方式：

GET

URL:

https://dummyjson.com/auth/me

### 测试目的

验证用户携带有效Token后是否可以访问受保护接口。

### 测试方法

认证测试

### 测试步骤

1. 用户登录获取accessToken
2. 在Authorization中添加Bearer Token
3. 请求用户信息接口

### 预期结果

1. 登录状态码200
2. 查询接口状态码200
3. 返回用户信息

### 实际结果

1. 登录状态码200
2. 查询接口状态码200
3. 返回用户信息

### 测试结果

Pass


## TC006 无Token访问用户信息

### 请求信息

请求方式：

GET

URL:

https://dummyjson.com/auth/me

### 测试目的

验证接口在未认证情况下是否能够正确拒绝访问。

### 测试方法

异常认证测试

### 测试步骤

1. 移除Authorization
2. 确认Cookie不存在
3. 请求接口

### 预期结果

1. 返回401状态码
2. 不返回用户信息
3. 提示缺少Token

### 实际结果

1. 状态码401
2. 未返回用户信息
3. 返回认证失败提示

### 测试结果

Pass