def fmt_number(num, is_pct=False):
    
    B = 10 ** 9
    M = 10 ** 6
    K = 10 ** 3
    
    if num >= B:
        num, unit = num / B, 'B'
    elif num >= 10 ** 6:
        num, unit = num / M, 'M'            
    elif num >= 10 ** 3:
        num, unit = num / K, 'K'            
    elif num <= 10 ** 3:
        num, unit = int(num), ''
    else: 
        unit = ''
        
    # Remove .0 from label
    label = f'{num:.1f}{unit}'
    label = label.replace('.0', '')
    
    return label

def fmt_pct(pct):

    pct = round(pct, 2)
    label = f'{pct:.1f}%'    

    return label

def get_vlines(ymin, ymax, k=4, shift=0):
    """

    Calculate and format y ticks and y labels.

    """
        
    dy = (ymax - ymin)
    yticks = [shift + i / k * dy for i in range(0, k + 1)]
    ylabels = [ fmt_number(y) for y in yticks]
    
    return yticks, ylabels