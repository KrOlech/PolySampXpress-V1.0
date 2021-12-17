def extend_map_exeqiute_old(self, test_extend, ofset, borderofset, dx, dy, tx, ty, fx, fy):

        x, y, z = self.frame_2.shape  # wymiary podglondu

        xm, ym, zm = self.map.shape  # wymiary aktualnej mapy

        if test_extend:
            tab = np.ones((xm + dx[0], ym+dy[0], zm), dtype=np.uint8)
            borderofset = ofset
            tab[dx[1]:xm + dx[1], dy[1]:ym+dy[1]] = self.map # Wkopoiowanie istniejocej mapy
        else:
            tab = self.map

        try:
            tab[tx[0]:tx[1], ty[0]:ty[1]] = self.frame_2[fx[0]:fx[1], fy[0]:fy[1]]
            print(tx[0],tx[1], ty[0],ty[1])
        except ValueError as e:
            print(e)
            print(tab[tx[0]:tx[1], ty[0]:ty[1]].shape, "map")
            print(self.frame_2[fx[0]:fx[1], fy[0]:fy[1]].shape,"frame")
        
        
        self.map = tab

    def extend_map_right(self):

        x, y, z = self.frame_2.shape  # wymiary podglondu

        xm, ym, zm = self.map.shape  # wymiary aktualnej mapy
        
        tx1 = self.ofsetx-self.ofsetxmax if self.ofsetx-self.ofsetxmax > 0 else self.ofsetx-self.ofsetxmax-768
        tx2 = x+self.ofsetx-self.ofsetxmin if x+self.ofsetx-self.ofsetxmin > 0 else x+self.ofsetx-self.ofsetxmin-768
        tx = (tx1,tx2)
        
        self.extend_map_exeqiute(self.ofsety > self.ofsetymax, self.ofsety+514, self.ofsetymax,
                                 (0,0), (self.delta_pixeli,0),
                                  tx,
                                 (ym, ym+self.delta_pixeli),
                                 (0, x),
                                 (y-self.delta_pixeli, y))

    def extend_map_dwn(self):
       
        x, y, z = self.frame_2.shape  # wymiary podglondu
        
        ty1 = self.ofsety-self.ofsetymin if self.ofsety-self.ofsetymin > 0 else self.ofsety-self.ofsetymin-1028
        ty2 = y + self.ofsety-self.ofsetymin if y + self.ofsety-self.ofsetymin > 0 else y + self.ofsety-self.ofsetymin-1024
        ty = (ty1,ty2)

        self.extend_map_exeqiute(self.ofsetx < self.ofsetxmin ,self.ofsetx+258, self.ofsetxmin,
                                (self.delta_pixeli,self.delta_pixeli), (0,0),
                                (0, self.delta_pixeli),
                                ty,
                                (0, self.delta_pixeli),
                                (0, y))

    def extend_map_left(self):

        x, y, z = self.frame_2.shape  # wymiary podglondu

        xm, ym, zm = self.map.shape  # wymiary aktualnej mapy
        
        tx1 = self.ofsetx-self.ofsetxmax if self.ofsetx-self.ofsetxmax > 0 else self.ofsetx-self.ofsetxmax-768
        tx2 = x+self.ofsetx-self.ofsetxmin if x+self.ofsetx-self.ofsetxmin > 0 else x+self.ofsetx-self.ofsetxmin-768
        tx = (tx1,tx2)

        self.extend_map_exeqiute(self.ofsety < self.ofsetymin, self.ofsety+514, self.ofsetymin,
                                 (0,0),(self.delta_pixeli,self.delta_pixeli),
                                 tx,
                                 (0, self.delta_pixeli),
                                 (0, x),
                                 (0, self.delta_pixeli))

    def extend_map_up(self):

        x, y, z = self.frame_2.shape  # wymiary podglondu
        
        xm, ym, zm = self.map.shape  # wymiary aktualnej mapy
        
        ty1 = self.ofsety-self.ofsetymin if self.ofsety-self.ofsetymin > 0 else self.ofsety-self.ofsetymin-1028
        ty2 = y + self.ofsety-self.ofsetymin if y + self.ofsety-self.ofsetymin > 0 else y + self.ofsety-self.ofsetymin-1024
        ty = (ty1,ty2)
        
        self.extend_map_exeqiute(self.ofsetx > self.ofsetxmax, self.ofsetx+258,  self.ofsetxmax,
                                 (self.delta_pixeli,0), (0,0),
                                 (xm, self.delta_pixeli+xm),
                                 ty,
                                 (x-self.delta_pixeli, x),
                                 (0, y))

    def extend_map_multi(self):

        dy = abs(self.dyp)
        dx = abs(self.dxp)

        x, y, z = self.frame_2.shape  # wymiary podglondu

        xm, ym, zm = self.map.shape  # wymiary aktualnej mapy
    
        try:
            if self.dyp > 0:
                print('right')
                self.mape_impute_tab[self.ofsetx - self.ofsetxmin: x + self.ofsetx - self.ofsetxmin, ym: ym + dy] = \
                    self.frame_2[:, y - dy:]
            else:
                print('left')
                self.mape_impute_tab[self.ofsetx - self.ofsetxmin: x + self.ofsetx - self.ofsetxmin, 0: dy] = \
                    self.frame_2[:, 0:dy]

            if self.dxp > 0:
                print('up')
                self.mape_impute_tab[xm: dx + xm, self.ofsety - self.ofsetymin: y + self.ofsety - self.ofsetymin] = \
                    self.frame_2[x - dx:, :]
            else:
                print('dwn')
                self.mape_impute_tab[0:dx, self.ofsety - self.ofsetymin: y + self.ofsety - self.ofsetymin] = \
                    self.frame_2[0:dx, :]

            self.map = self.mape_impute_tab
        except Exception as e:
            print(e)
        #metoda generujaca pusty
    def map_size_update(self):

        xm, ym, zm = self.map.shape

        if self.ofsetx < self.ofsetxmin:
            xm += abs(self.dxp)
            self.ofsetxmin = self.ofsetx
        elif self.ofsetx > self.ofsetxmax:
            xm += abs(self.dxp)
            self.ofsetxmax = self.ofsetx
        else:
            pass

        if self.ofsety < self.ofsetymin:
            ym += abs(self.dyp)
            self.ofsetymin = self.ofsety
        elif self.ofsety > self.ofsetymax:
            ym += abs(self.dyp)
            self.ofsetymax = self.ofsety
        else:
            pass

        return np.ones((xm, ym, zm), dtype=np.uint8)

    def inject_map(self):

        xm, ym, zm = self.map.shape
        try:
            if self.dxp >= 0 and  self.dyp >= 0:
                self.mape_impute_tab[:xm, :ym] = self.map

            elif self.dxp<0 and  self.dyp >= 0:
                self.mape_impute_tab[self.dxp:, :ym] = self.map

            elif self.dxp>=0 and  self.dyp < 0:
                self.mape_impute_tab[:xm, self.dyp:] = self.map

            elif self.dxp<0 and  self.dyp < 0:
                self.mape_impute_tab[self.dxp:, self.dyp:] = self.map
        except Exception as e:
            print(e)
    #update map on center on click metod WIP
    def mapupdate(self):
    
        self.save_curent_viue()

        self.mape_impute_tab = self.map_size_update()

        print(self.dxp, self.dyp)

        self.inject_map()

        self.whot_to_drow = 'viue_muve'
        self.direction_change = 'multi'
        self.update()
