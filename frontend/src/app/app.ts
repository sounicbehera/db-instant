import { HttpClient } from '@angular/common/http';
import { Component, computed, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

type ApiEngine = 'postgres' | 'mysql';
type DbEngine = 'PostgreSQL' | 'MySQL';
type DbStatus = 'Active' | 'Provisioning' | 'Stopping';

type ApiDatabase = {
  id: number;
  instance_name: string;
  engine_type: ApiEngine;
  username: string;
  password: string;
  connection_string: string;
  status: string;
};

type DatabaseInstance = {
  id: number;
  name: string;
  engine: DbEngine;
  status: DbStatus;
  connectionString: string;
  cpu: string;
  memory: string;
  createdAt: string;
};

@Component({
  selector: 'app-root',
  imports: [FormsModule],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App implements OnInit {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = 'http://localhost:8000/api/databases';

  protected readonly instances = signal<DatabaseInstance[]>([]);
  protected readonly isLoading = signal(false);
  protected readonly errorMessage = signal('');
  protected readonly showModal = signal(false);
  protected readonly newName = signal('feature-test-db');
  protected readonly newEngine = signal<DbEngine>('PostgreSQL');

  protected readonly activeCount = computed(
    () => this.instances().filter((db) => db.status === 'Active').length,
  );

  ngOnInit(): void {
    this.loadDatabases();
  }

  protected openModal(): void {
    this.showModal.set(true);
  }

  protected closeModal(): void {
    this.showModal.set(false);
  }

  protected createDatabase(): void {
    const instanceName = this.newName().trim() || 'sandbox-db';
    const engineType = this.toApiEngine(this.newEngine());

    this.errorMessage.set('');
    this.isLoading.set(true);

    this.http
      .post<ApiDatabase>(this.apiUrl, {
        instance_name: instanceName,
        engine_type: engineType,
      })
      .subscribe({
        next: (database) => {
          this.instances.update((items) => [this.fromApiDatabase(database), ...items]);
          this.closeModal();
          this.isLoading.set(false);
        },
        error: () => {
          this.errorMessage.set('Could not create database. Check that FastAPI is running on port 8000.');
          this.isLoading.set(false);
        },
      });
  }

  protected deleteDatabase(id: number): void {
    this.errorMessage.set('');
    this.http.delete(`${this.apiUrl}/${id}`).subscribe({
      next: () => {
        this.instances.update((items) => items.filter((db) => db.id !== id));
      },
      error: () => {
        this.errorMessage.set('Could not delete database. Check the backend logs.');
      },
    });
  }

  protected connectionString(db: DatabaseInstance): string {
    return db.connectionString;
  }

  private loadDatabases(): void {
    this.isLoading.set(true);
    this.errorMessage.set('');

    this.http.get<ApiDatabase[]>(this.apiUrl).subscribe({
      next: (databases) => {
        this.instances.set(databases.map((database) => this.fromApiDatabase(database)));
        this.isLoading.set(false);
      },
      error: () => {
        this.errorMessage.set('Could not load databases. Start FastAPI on port 8000, then refresh.');
        this.isLoading.set(false);
      },
    });
  }

  private fromApiDatabase(database: ApiDatabase): DatabaseInstance {
    return {
      id: database.id,
      name: database.instance_name,
      engine: database.engine_type === 'postgres' ? 'PostgreSQL' : 'MySQL',
      status: database.status === 'active' ? 'Active' : 'Provisioning',
      connectionString: database.connection_string,
      cpu: '0.5 CPU',
      memory: '512 MB',
      createdAt: 'From API',
    };
  }

  private toApiEngine(engine: DbEngine): ApiEngine {
    return engine === 'PostgreSQL' ? 'postgres' : 'mysql';
  }
}