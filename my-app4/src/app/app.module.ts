import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { HttpClientModule } from '@angular/common/http';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HeroesComponent } from './heroes/heroes.component';

import { HttpClientInMemoryWebApiModule } from 'angular-in-memory-web-api';
import { InMemoryDataService } from './in-memory-data.service';
import { CellComponent } from './cell/cell.component';
import { EngComponent } from './eng/eng.component';


@NgModule({
  declarations: [
    AppComponent,
    HeroesComponent,
    CellComponent,
    EngComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,


// The HttpClientInMemoryWebApiModule module intercepts HTTP requests
// and returns simulated server responses.
// Remove it when a real server is ready to receive requests.

  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
