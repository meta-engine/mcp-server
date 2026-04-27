/** Aggregate root representing a stock item in the inventory. */
export class StockItem {
  constructor(
    public readonly id: string,
    public readonly createdAt: Date,
    public readonly updatedAt: Date,
    public readonly name: string,
    public readonly description: string,
  ) {}
}
