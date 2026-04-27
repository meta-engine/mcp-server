/** Aggregate root representing a physical shipment. */
export class Shipment {
  constructor(
    public readonly id: string,
    public readonly createdAt: Date,
    public readonly updatedAt: Date,
    public readonly name: string,
    public readonly description: string,
  ) {}
}
