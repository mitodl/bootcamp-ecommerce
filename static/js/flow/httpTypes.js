export type HttpResponse<T> = {
  body: T|{
    errors: string|Array<string>
  },
  status: number
}
