def get_vlines(ymin, ymax, k=4, shift=0):
    """

    Calculate and format y ticks and y labels.

    """

    def fmt_ytick(y):
        
        B = 10 ** 9
        M = 10 ** 6
        K = 10 ** 3
        
        if y >= B:
            y, u = y / B, 'B'
        elif y >= 10 ** 6:
            y, u = y / M, 'M'            
        elif y >= 10 ** 3:
            y, u = y / K, 'K'            
        elif y <= 10 ** 3:
            y, u = int(y), ''
        else: 
            u = ''
            
        # Remove .0 from label
        label = f'{y:.1f}{u}'
        label = label.replace('.0', '')
        return label
        
    dy = (ymax - ymin)
    yticks = [shift + i / k * dy for i in range(0, k + 1)]
    ylabels = [ fmt_ytick(y) for y in yticks]
    
    return yticks, ylabels