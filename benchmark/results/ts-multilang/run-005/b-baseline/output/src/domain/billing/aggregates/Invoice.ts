/** Aggregate root for an invoice. */
export class Invoice {
  constructor(
    public readonly id: string,
    public readonly createdAt: Date,
    public readonly updatedAt: Date,
    public readonly name: string,
    public readonly description: string,
  ) {}
}
