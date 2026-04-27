/** Event aggregate root for the analytics domain. */
export class Event {

  constructor(public id: string, public createdAt: Date, public updatedAt: Date, public name: string, public description: string) { }
}
