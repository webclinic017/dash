import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import {CellComponent} from './cell/cell.component'
import {EngComponent} from './eng/eng.component'


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
    }


    ];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
