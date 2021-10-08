import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import {CellComponent} from './cell/cell.component'
import {EngComponent} from './eng/eng.component'
import {SerComponent} from './ser/ser.component'

const routes: Routes = [

    {
      path:'',
      component: CellComponent
    } ,
    {
      path:'cell',
      component: CellComponent
    } ,
    {
     path:'eng',
     component: EngComponent
    } ,
    {
     path:'ser',
     component: SerComponent
    }

    ];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
