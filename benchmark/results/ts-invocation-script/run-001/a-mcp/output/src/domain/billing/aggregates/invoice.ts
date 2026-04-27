/** Invoice aggregate root for the billing domain. */
export class Invoice {

  constructor(public id: string, public createdAt: Date, public updatedAt: Date, public name: string, public description: string) { }
}
