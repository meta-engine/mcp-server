/** Aggregate root representing a user in the identity domain. */
export class User {
  constructor(
    public readonly id: string,
    public readonly createdAt: Date,
    public readonly updatedAt: Date,
    public readonly name: string,
    public readonly description: string,
  ) {}
}
