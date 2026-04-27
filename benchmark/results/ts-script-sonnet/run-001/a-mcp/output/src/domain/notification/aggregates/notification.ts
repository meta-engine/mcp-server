/** Notification aggregate root for the notification domain. */
export class Notification {

  constructor(public id: string, public createdAt: Date, public updatedAt: Date, public name: string, public description: string) { }
}
