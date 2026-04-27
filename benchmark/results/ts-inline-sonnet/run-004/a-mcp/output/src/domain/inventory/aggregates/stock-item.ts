/** StockItem aggregate root for the inventory domain. */
export class StockItem {

  constructor(public id: string, public createdAt: Date, public updatedAt: Date, public name: string, public description: string) { }
}
