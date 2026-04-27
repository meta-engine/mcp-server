/** User aggregate root for the identity domain. */
export class User {

  constructor(public id: string, public createdAt: Date, public updatedAt: Date, public name: string, public description: string) { }
}
