import { Event } from "../aggregates/Event";

/** Service EventRepository. */
export class EventRepository {
  create(input: Partial<Event>): Event {
    void input;
    throw new Error("not implemented");
  }
  findById(id: string): Event | null {
    void id;
    throw new Error("not implemented");
  }
  list(limit: number): Event[] {
    void limit;
    throw new Error("not implemented");
  }
  delete(id: string): void {
    void id;
    throw new Error("not implemented");
  }
}
