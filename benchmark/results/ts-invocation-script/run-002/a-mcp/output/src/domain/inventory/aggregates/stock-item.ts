/** StockItem aggregate root for the inventory domain. */
export class StockItem {

  constructor(public id: string, public createdAt: Date1, public updatedAt: Date2, public name: string, public description: string) { }
}
