/** Product aggregate root for the catalog domain. */
export class Product {

  constructor(public id: string, public createdAt: Date, public updatedAt: Date, public name: string, public description: string) { }
}
