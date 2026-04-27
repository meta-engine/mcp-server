/** Shipment aggregate root for the shipping domain. */
export class Shipment {

  constructor(public id: string, public createdAt: Date, public updatedAt: Date, public name: string, public description: string) { }
}
