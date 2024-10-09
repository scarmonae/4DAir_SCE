import matplotlib.pyplot as plt
import numpy as np
import os 
import matplotlib.dates as mdates
import matplotlib as mpl

def site_location(lat=0, lon=0):
  sites = {(48.44424057006836, -4.4123148918151855): 'Brest', 
           (48.77284622192383, 2.012406349182129): 'Trappes',
           (-75.6, 6.2): "Medellín"}
  try:
    return sites[(lat, lon)]
  except:
    # return 'Not known site'
    return 'Brest'

def title1(mytitle, coef):
    """
    inclus le titre au document.
        @param mytitle: titre du document.
        @param coef : coefficient GFAT (renvoye par la fonction formatGFAT).
    """

    plt.figtext(0.5, 0.95, mytitle, fontsize=6.5*coef, fontweight='bold',
                horizontalalignment='center', verticalalignment='center')
    return


def title2(mytitle, coef):
    """
    inclus le sous titre au document.
        @param mytitle: titre du document.
        @param coef : coefficient GFAT (renvoye par la fonction formatGFAT).
    """

    plt.figtext(0.5, 0.89, mytitle, fontsize=5.5*coef,
                horizontalalignment='center', verticalalignment='center')
    return


def title3(mytitle, coef):
    """
    inclus le sous sous titre au document.
        @param mytitle: titre du document.
        @param coef : coefficient GFAT (renvoye par la fonction formatGFAT).
    """
    plt.figtext(0.5, 0.85, mytitle, fontsize=4.5*coef,
                horizontalalignment='center', verticalalignment='center')
    return

def gapsizer(ax, time, range, gapsize, colour='#c7c7c7'):
    """
    This function creates a rectangle of color 'colour' when time gap 
    are found in the array 'time'. 
    """
        # search for holes in data
    # --------------------------------------------------------------------
    dif_time = time[1:] - time[0:-1]
    print(type(dif_time))
    for index, delta in enumerate(dif_time):
        # pdb.set_trace()
        if delta > np.timedelta64(gapsize, 'm'):
            # missing hide bad data
            start = mdates.date2num(time[index])
            end = mdates.date2num(time[index + 1])
            width = end - start

            # Plot rectangle
            end = mdates.date2num(time[index + 1])
            rect = mpl.patches.Rectangle(
                (start, 0), width, np.nanmax(range),
                color=colour)
            ax.add_patch(rect)

def plot_as_me(ds, channel, axes, qt, wl, signal_mode, attrs, save_fig=False, coef=1, fixed_time_range=True, **kwargs):
    """
    Modificación para permitir que los valores por debajo del mínimo tengan un color más oscuro.
    @param ds: dataset de xarray con los datos.
    @param channel: canal de datos a graficar.
    @param axes: objeto de ejes para graficar.
    @param qt, wl, signal_mode: configuración de título.
    @param attrs: atributos del dataset (como la latitud y longitud).
    @param save_fig: opción para guardar la figura.
    @param coef: coeficiente de ajuste para el tamaño del texto.
    @param fixed_time_range: Si es True, fija el eje x entre 00:00 y 23:59, de lo contrario usa los límites de los datos.
    """

    # Configuración de color del gráfico
    cmap = mpl.cm.jet
    bounds = np.linspace(0, 100, 64)
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

    # Establecer un color más oscuro para los valores menores al mínimo (0)
    cmap.set_under('darkblue')  # Puedes ajustar este color como prefieras
    vmin = kwargs.get('vmin', 0)  # El valor mínimo es 0 por defecto, pero puedes cambiarlo al pasar un argumento

    # Títulos
    title1('LiMON {mode} at {wl} {wlu}'.format(instr="LiMON", mode=signal_mode, qt=qt, wl=wl, wlu='nm'), coef=2.5*coef)
    title2(str(ds.time.values[0].astype('datetime64[D]')), coef=3*coef)
    title3('{} ({:.1f}N, {:.1f}E)'.format(site_location(float(attrs["Latitude_degrees_north"]), float(attrs["Longitude_degrees_east"])), 
                                           float(attrs["Latitude_degrees_north"]), 
                                           float(attrs["Longitude_degrees_east"])), coef=3*coef)

    # Graficar el canal de datos
    try:
        q = ds[channel].sel(range=slice(0, 5000), channels=0).plot.pcolormesh(x='time', y='range', cmap=cmap, 
                                                                             vmin=vmin, vmax=kwargs['vmax'])
    except:
        q = ds[channel].sel(range=slice(0, 5000)).plot.pcolormesh(x='time', y='range', cmap=cmap, 
                                                                  vmin=vmin, vmax=kwargs['vmax'])

    # Configuración de la barra de color
    q.colorbar.ax.tick_params(labelsize=14*coef)
    
    # Ajustar márgenes
    plt.subplots_adjust(left=0, bottom=0, right=1, top=0.8, wspace=0, hspace=0)
    
    # Formato del eje x (tiempo)
    myFmt = mdates.DateFormatter('%Hh')
    axes.xaxis.set_major_formatter(myFmt)
    
    # Crear parches para huecos en los datos
    gapsizer(axes, ds.time.values, ds.range, gapsize=5, colour='#c7c7c7')
    
    # Configurar límites del eje X
    if fixed_time_range:
        # Si se selecciona un rango fijo, ajustamos entre 00:00 y 23:59
        start_time = ds.time[0].values.astype('datetime64[D]')
        end_time = start_time + np.timedelta64(1, 'D')
        axes.set_xlim([start_time, end_time])
    else:
        # Si no, ajustamos el rango al de los datos
        axes.set_xlim([ds.time.values.min(), ds.time.values.max()])

    # Configurar colores fuera del rango
    q.cmap.set_over('white')

    # Guardar la figura si es necesario
    if save_fig:
        year, month, day = str(ds.time[0].values.astype('datetime64[D]')).split('-') 
        out_dir = '/content/drive/MyDrive/TRABAJO DE GRADO - SCE/Proyecto Avanzado II/Workbench/output_dir/images'
        fl_name = '{instru}_{qt}_{wl}_{mode}_mode_{y}{m}{d}.jpg'.format(instru=attrs['system'], qt=qt, wl=wl, mode=signal_mode, y=year, m=month, d=day)
        fl_name = os.path.join(out_dir, fl_name)
        plt.savefig(fl_name, dpi=200)
