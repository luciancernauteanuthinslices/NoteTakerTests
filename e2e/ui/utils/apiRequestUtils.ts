import { APIRequestContext, APIResponse } from '@playwright/test';

export async function executeRequest(
  apiContext: APIRequestContext,
  requestUrl: string,
  method: 'get' | 'post' | 'put' | 'patch' | 'delete',
  requestOptions: object
): Promise<APIResponse> {
  let response: APIResponse;

  try {
    switch (method) {
      case 'get':
        response = await apiContext.get(requestUrl, requestOptions);
        break;
      case 'post':
        response = await apiContext.post(requestUrl, requestOptions);
        break;
      case 'put':
        response = await apiContext.put(requestUrl, requestOptions);
        break;
      case 'patch':
        response = await apiContext.patch(requestUrl, requestOptions);
        break;
      case 'delete':
        response = await apiContext.delete(requestUrl, requestOptions);
        break;
    }

    if (!response.ok()) {
      const errorStatus = `Code: ${response.status()} \r\n`;
      const responseStatus = `Status: ${response.ok()} \r\n`;
      const errorResponse = `Response: ${await response.text()} \r\n`;
      throw `${errorStatus} ${errorResponse} ${responseStatus} `;
    }

    return response;

  } catch (error) {
    const errorRequestUrl = `Request url: ${requestUrl} \r\n`;
    const errorRequestMethod = `Method: ${method} \r\n`;
    const errorRequestOptions = `Request options: ${JSON.stringify(requestOptions)} \r\n`;

    throw new Error(
      `Invalid request! Failed on 'executeRequest' method. \r\n ${errorRequestUrl} ${errorRequestMethod} ${errorRequestOptions} ${error}`
    );
  }
}
